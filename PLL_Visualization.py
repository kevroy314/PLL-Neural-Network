from pyqtgraph.Qt import QtGui, QtCore # For GUI
import numpy as np # For matrix computation
import pyqtgraph as pg # for GUI
from biquad_module import Biquad # For filters
from pylab import * # For PLL
import random, re # For noise

# Set up application window
app = QtGui.QApplication([])
win = pg.GraphicsWindow(title="PLL Example Animated")
win.resize(1000,600)
win.setWindowTitle('PLL Example Animated')
pg.setConfigOptions(antialias=True)

# Set up plot environment
plotArea = win.addPlot()
curves = []
curves.append(plotArea.plot(pen=(255,0,0)))
curves.append(plotArea.plot(pen=(0,255,0)))
curves.append(plotArea.plot(pen=(0,0,255)))
curves.append(plotArea.plot(pen=(255,255,255)))

# Class representing the functioning of a PLL
class PLL:
    def __init__(self, sample_rate, carrier_frequency, deviation, loop_gain):
        self.invsqr2 = 1.0 / sqrt(2.0)

        self.sample_rate = sample_rate
        self.start_f = carrier_frequency - deviation
        self.end_f = carrier_frequency + deviation

        self.pll_integral = 0
        self.old_ref = 0
        self.pll_cf = carrier_frequency
        self.pll_loop_gain = loop_gain
        self.ref_sig = 0

        self.pll_loop_control = 0
        self.output = 0
        self.pll_lock = 0
        self.logic_lock = 0

        self.loop_lowpass = Biquad(Biquad.LOWPASS,100,self.sample_rate,self.invsqr2)
        self.output_lowpass = Biquad(Biquad.LOWPASS,10,self.sample_rate,self.invsqr2)
        self.lock_lowpass = Biquad(Biquad.LOWPASS,10,self.sample_rate,self.invsqr2)

        self.da = []
        self.db = []
        self.dc = []

    def update(self, t, y):
        # BEGIN PLL block
        self.pll_loop_control = y * self.ref_sig * self.pll_loop_gain # phase detector
        self.pll_loop_control = self.loop_lowpass(self.pll_loop_control) # loop low-pass filter
        self.output = self.output_lowpass(self.pll_loop_control) # output low-pass filter
        self.pll_integral += self.pll_loop_control / self.sample_rate # FM integral
        self.ref_sig = cos(2 * pi * self.pll_cf * (t + self.pll_integral)) # reference signal
        self.quad_ref = (self.ref_sig - self.old_ref) * self.sample_rate / (2 * pi * self.pll_cf) # quadrature reference
        self.old_ref = self.ref_sig
        self.pll_lock = self.lock_lowpass(-self.quad_ref * y) # lock sensor
        self.logic_lock = (0,1)[self.pll_lock > 0.1] # logical lock
        # END PLL block
        self.da.append(self.output * 32)
        self.db.append(self.pll_lock * 2)
        self.dc.append(self.logic_lock)

# Class representing a test signal to be fed to the PLL
class TestSignal:
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

# Simulation Properties
sample_rate = 40000.0
carrier_frequency = 2000
deviation = 140

# PLL Properties
loop_gain = 0.05

# Create PLL
pll = PLL(sample_rate, carrier_frequency, deviation, loop_gain)

# Test Signal Properties
noise_level = 1
duration = 1

# Test input signal variables
test_signal = TestSignal(sample_rate, carrier_frequency, deviation, noise_level, duration)

# Time counter
t = 0
tick = 1/sample_rate

# Decimation for the display to speed up computation
display_decimation = 1000
frame_counter = 0

# Create loop timer
timer = QtCore.QTimer()

def update():
    global timer, curves, plotArea, t, tick, frame_counter, duration, pll, test_signal

	# Stop the simulation when the duration has completed
    if t >= duration:
        timer.stop()

    # Update the test signal and the ppl (iterate simulation)
    pll.update(t, test_signal.update(t))

    # Graph the PLL states according to the display decimation
    if frame_counter%display_decimation == 0:
        curves[0].setData(pll.da)
        curves[1].setData(pll.db)
        curves[2].setData(pll.dc)

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
