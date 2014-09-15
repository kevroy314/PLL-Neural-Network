from pyqtgraph.Qt import QtGui, QtCore # For GUI
import numpy as np # For matrix computation
import pyqtgraph as pg # for GUI
from biquad_module import Biquad # For filters
from pylab import * # For PLL
import random, re # For noise
from scipy import signal
from collections import deque

# Set up application window
app = QtGui.QApplication([])
win = pg.GraphicsWindow(title="PLL Example Animated")
win.resize(1000,600)
win.setWindowTitle('PLL Example Animated')
pg.setConfigOptions(antialias=True)

# Set up plot environment
plotArea = win.addPlot()
plotArea.enableAutoRange('xy',True)
curves = []
curves.append(plotArea.plot(pen=(255,0,0)))
curves.append(plotArea.plot(pen=(0,255,0)))
curves.append(plotArea.plot(pen=(0,0,255)))
curves.append(plotArea.plot(pen=(255,255,255)))

legend = pg.LegendItem(offset=(0,1))
legend.addItem(curves[0], "Phase Detected, Lowpass Filtered")
legend.addItem(curves[1], "PLL Lock")
legend.addItem(curves[2], "Logical Lock")
legend.addItem(curves[3], "Test Signal")
legend.setParentItem(plotArea)

# Class representing the functioning of a PLL
# Sample Rate is in Hz
# Carrier Frequency is in Hz
# Deviation is in Hz
# Loop Gain is a proportion (usually 0<x<1)
# Phase Shift is a proportion (usually 0<=x<1)
class PLL:
    def __init__(self, sample_rate, carrier_frequency, loop_gain, phase_shift):
        self.invsqr2 = 1.0 / sqrt(2.0)

        self.sample_rate = sample_rate

        self.phase_shift = phase_shift

        self.pll_integral = 0
        self.old_ref = 0
        self.pll_cf = carrier_frequency
        self.pll_loop_gain = loop_gain
        self.ref_sig = 0

        self.pll_loop_control = 0
        self.output = 0
        self.pll_lock = 0
        self.logic_lock = 0

        #self.loop_lowpass = Biquad(Biquad.LOWPASS,100,self.sample_rate,self.invsqr2)
        #self.output_lowpass = Biquad(Biquad.LOWPASS,10,self.sample_rate,self.invsqr2)
        #self.lock_lowpass = Biquad(Biquad.LOWPASS,10,self.sample_rate,self.invsqr2)

        self.loop_lowpass_data = deque()
        self.output_lowpass_data = deque()
        self.lock_lowpass_data = deque()
        self.window_size = 1000
        self.filter_order = 2

        self.da = []
        self.db = []
        self.dc = []

    def butter_lowpass(self, lowcut, fs, order=5):
        nyq = 0.5 * fs
        low = lowcut / nyq
        b, a = signal.butter(order, low, btype='low')
        return b, a

    def butter_lowpass_filter(self, data, lowcut, fs, order=5):
        b, a = self.butter_lowpass(lowcut, fs, order=order)
        y = signal.lfilter(b, a, data)
        return y

    def update(self, t, y):
        # BEGIN PLL block
        self.pll_loop_control = y * self.ref_sig * self.pll_loop_gain # phase detector

        self.loop_lowpass_data.append(self.pll_loop_control)
        if(len(self.loop_lowpass_data) > self.window_size):
            self.loop_lowpass_data.popleft()
        self.pll_loop_control = self.butter_lowpass_filter(self.loop_lowpass_data, 100, self.sample_rate, order=self.filter_order)[-1] # loop low-pass filter
        self.output_lowpass_data.append(self.pll_loop_control)
        if(len(self.output_lowpass_data) > self.window_size):
            self.output_lowpass_data.popleft()
        self.output = self.butter_lowpass_filter(self.output_lowpass_data, 10, self.sample_rate, order=self.filter_order)[-1] # output low-pass filter

        self.pll_integral += self.pll_loop_control / self.sample_rate # FM integral
        self.ref_sig = cos(2 * pi * self.pll_cf * (t + self.pll_integral) + (self.phase_shift * 2 * pi)) # reference signal
        self.quad_ref = (self.ref_sig - self.old_ref) * self.sample_rate / (2 * pi * self.pll_cf) # quadrature reference
        self.old_ref = self.ref_sig

        self.lock_lowpass_data.append(-self.quad_ref * y)
        if(len(self.lock_lowpass_data) > self.window_size):
            self.lock_lowpass_data.popleft()
        self.pll_lock = self.butter_lowpass_filter(self.lock_lowpass_data, 10, self.sample_rate, order=self.filter_order)[-1] # lock sensor
        self.logic_lock = (0,1)[self.pll_lock > 0.1] # logical lock
        # END PLL block
        self.da.append(self.output)
        self.db.append(self.pll_lock)
        self.dc.append(self.logic_lock)

# Class representing a test signal to be fed to the PLL
class SweepSignal:
    def __init__(self, sample_rate, carrier_frequency, deviation, noise_level, duration):
        self.fa = []
        self.modi = 0
        self.duration = duration
        self.carrier_frequency = carrier_frequency
        self.deviation = deviation
        self.sample_rate = sample_rate
        self.noise_level = noise_level

    def ntrp(self,x,xa,xb,ya,yb):
        return (x-xa) * (yb-ya) / (xb-xa) + ya

    def update(self, t):
        sweep_freq = self.ntrp(t, 0, self.duration, self.carrier_frequency - self.deviation, self.carrier_frequency + self.deviation)
        self.fa.append(sweep_freq)
        self.modi += (sweep_freq - self.carrier_frequency) / (self.carrier_frequency * self.sample_rate)
        test_sig = cos(2 * pi * self.carrier_frequency * (t + self.modi))
        noise = random.random() * 2 - 1
        test_sig += noise * self.noise_level 
        return test_sig

class SineSignal:
    def __init__(self, amplitude, frequency, phase, noise_level):
        self.frequency = frequency
        self.two_pi_frequency = 2 * pi * frequency
        self.amplitude = amplitude
        self.phase = phase * 2 * pi
        self.noise_level = noise_level
        self.fa = []
        self.fa_scaling = 0.001

    def update(self, t):
        test_sig = self.amplitude * sin(t * self.two_pi_frequency + self.phase) + ((random.random() * 2 - 1) * self.noise_level)
        self.fa.append(test_sig * self.fa_scaling)
        return test_sig

# Simulation Properties
sample_rate = 1000.0
carrier_frequency = 2000
deviation = 140

# PLL Properties
loop_gain = 0.05
phase_shift = 0.0
number_of_PLLs = 1
PLLs = []

# Create PLL
for i in range(0, number_of_PLLs):
    PLLs.append(PLL(sample_rate, carrier_frequency, loop_gain, phase_shift))

# Test Signal Properties
noise_level = 1
duration = 4
test_signals = []

# Test input signal variables
for i in range(0, number_of_PLLs):
    test_signals.append(SineSignal(1, 10, 0, noise_level))
    #test_signals.append(SweepSignal(sample_rate, carrier_frequency, deviation, noise_level, duration))

# Time counter
t = 0
tick = 1/sample_rate

# Decimation for the display to speed up computation
display_decimation = 100
frame_counter = 0
display_pll_num = 0

# Create loop timer
timer = QtCore.QTimer()

def update():
    global timer, curves, plotArea, t, tick, frame_counter, duration, PLLs, test_signals

	# Stop the simulation when the duration has completed
    if t >= duration:
        timer.stop()

    # Update the test signal and the ppl (iterate simulation)
    for i in range(0,number_of_PLLs):
        PLLs[i].update(t, test_signals[i].update(t))

    # Graph the PLL states according to the display decimation
    if frame_counter%display_decimation == 0:
        curves[0].setData(PLLs[display_pll_num].da)
        curves[1].setData(PLLs[display_pll_num].db)
        curves[2].setData(PLLs[display_pll_num].dc)
        curves[3].setData(test_signals[display_pll_num].fa)

    # Iterate the time counter according to the sample rate
    t += tick
    #Iterate the display frame counter
    frame_counter += 1

# Begin Simulation
timer.timeout.connect(update)
timer.start(0)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
