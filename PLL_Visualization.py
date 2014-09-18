from collections import deque
from decimal import *
from pyqtgraph.Qt import QtGui, QtCore  # For GUI
import pyqtgraph as pg  # For GUI
from pylab import *  # For PLL
from scipy import signal
import random


# Set up application window
app = QtGui.QApplication([])
win = pg.GraphicsWindow(title="PLL Example Animated")
win.resize(1000, 600)
win.setWindowTitle('PLL Example Animated')
pg.setConfigOptions(antialias=True)


# Class representing the functioning of a PLL
# Sample Rate is in Hz
# Carrier Frequency is in Hz
# Deviation is in Hz
# Loop Gain is a proportion (usually 0<x<1)
# Phase Shift is a proportion (usually 0<=x<1)
class PLL:
    def __init__(self, _sample_rate, _carrier_frequency, _voltage_gain, _phase_shift):
        self.sample_rate = _sample_rate

        self.current_phase_shift = 0
        self.next_phase_shift = 0
        self.persistent_phase_shift = _phase_shift

        self.carrier_frequency = _carrier_frequency
        self.voltage_gain = _voltage_gain

        self.voltage_output = 0

        self.voltage_output_lowpass_data = deque()
        self.window_size = 1000
        self.lowpass_cutoff_frequency = 10
        self.filter_order = 2

        self.output_log = []
        self.current_phase_shift_log = []
        self.control_log = []

    @staticmethod
    def butter_lowpass(_frequency_cutoff, _fs, order=5):
        nyq = 0.5 * _fs
        low = _frequency_cutoff / nyq
        b, a = signal.butter(order, low, btype='low')
        return b, a

    def butter_lowpass_filter(self, _data, _frequency_cutoff, _fs, order=5):
        b, a = self.butter_lowpass(_frequency_cutoff, _fs, order=order)
        return signal.lfilter(b, a, _data)

    @staticmethod
    def v(theta):
        return sin(theta)

    def update(self, _t, _y, _PLLs, _self_index, _weight_matrix, _connectivity_matrix):
        # BEGIN PLL block

        # Phase Detector
        control = 0
        if len(self.output_log) != 0:
            control = (_y * self.output_log[-1] * self.voltage_gain)
        self.control_log.append(control)

        # Lowpass Filter
        integral = self.butter_lowpass_filter(self.control_log, self.lowpass_cutoff_frequency,
                                              self.carrier_frequency, order=self.filter_order)[-1]

        # Determine Weighted Phase Adjustment
        phase_aggregator = 0
        for _j in range(0, len(PLLs)):
            v_ij = _connectivity_matrix[_self_index][_j] * cos(_weight_matrix[_self_index][_j]).real
            w_ij = _connectivity_matrix[_self_index][_j] * sin(_weight_matrix[_self_index][_j]).imag

            phase_aggregator += v_ij * self.v(_PLLs[_j].current_phase_shift - (pi / 2)) + \
                                w_ij * self.v(_PLLs[_j].current_phase_shift)

        self.next_phase_shift = (self.v(integral) * phase_aggregator)

        # Voltage Controlled Oscillator
        output = self.v(self.carrier_frequency * _t + (self.next_phase_shift + self.persistent_phase_shift))

        # END PLL block
        self.output_log.append(output)
        self.current_phase_shift_log.append(self.next_phase_shift)

        return output

    def apply_next_phase_shift(self):
        self.current_phase_shift = self.next_phase_shift


# Class representing a test signal to be fed to the PLL
class SweepSignal:
    def __init__(self, _sample_rate, _carrier_frequency, _deviation, _noise_level, _duration):
        self.signal_log = []
        self.modulus_i = 0
        self.duration = _duration
        self.carrier_frequency = _carrier_frequency
        self.deviation = _deviation
        self.sample_rate = _sample_rate
        self.noise_level = _noise_level

    @staticmethod
    def sweep_function_core(x, xa, xb, ya, yb):
        return (x - xa) * (yb - ya) / (xb - xa) + ya

    def update(self, _t):
        sweep_freq = self.sweep_function_core(_t, 0, self.duration,
                                              self.carrier_frequency - self.deviation,
                                              self.carrier_frequency + self.deviation)
        self.signal_log.append(sweep_freq)
        self.modulus_i += (sweep_freq - self.carrier_frequency) / (self.carrier_frequency * self.sample_rate)
        test_sig = cos(2 * pi * self.carrier_frequency * (_t + self.modulus_i))
        noise = random.random() * 2 - 1
        test_sig += noise * self.noise_level
        return test_sig


class SineSignal:
    def __init__(self, _amplitude, _frequency, _phase, _noise_level):
        self.frequency = _frequency
        self.two_pi_frequency = 2 * pi * _frequency
        self.amplitude = _amplitude
        self.phase = _phase * 2 * pi
        self.noise_level = _noise_level
        self.signal_log = []
        self.signal_log_scaling = 1

    def update(self, _t):
        test_sig = \
            self.amplitude * \
            sin(_t * self.two_pi_frequency + self.phase) + \
            ((random.random() * 2 - 1) * self.noise_level)
        self.signal_log.append(test_sig * self.signal_log_scaling)
        return test_sig

# Simulation Properties
sample_rate = 1000.0
carrier_frequency = 2000
deviation = 140

# PLL Properties
number_of_PLLs = 3

phase_weight_matrix = [
    [1, 0.2, 0],
    [0.2, 1, 0.4],
    [0, 0.4, 1]
]

connectivity_matrix = [
    [1, 1, 1],
    [1, 1, 1],
    [1, 1, 1]
]

if (np.array(phase_weight_matrix).transpose() != np.array(phase_weight_matrix)).any():
    print "Error: Phase Offset Matrix Not Symmetric Across Diagonal."
else:
    print "Array Symmetry Validated."
PLLs = []

# Create PLL
for i in range(0, number_of_PLLs):
    PLLs.append(PLL(sample_rate, carrier_frequency, 1, -1.57079))

# Test Signal Properties
noise_level = 0.01
duration = 4
test_signals = []

# Test input signal variables
for i in range(0, number_of_PLLs):
    test_signals.append(SineSignal(1, 1.2 * (i + 1), 0, noise_level))
    # test_signals.append(SweepSignal(sample_rate, carrier_frequency, deviation, noise_level, duration))

# Set up plot environment
plotAreas = []
curves = []
for i in range(0, number_of_PLLs):
    plotAreas.append(win.addPlot())
    win.nextRow()
    plotAreas[i].enableAutoRange('xy', True)
    curves.append(
        [plotAreas[i].plot(pen=(255, 0, 0)), plotAreas[i].plot(pen=(0, 255, 0)), plotAreas[i].plot(pen=(0, 0, 255)),
         plotAreas[i].plot(pen=(255, 255, 255))])

    legend = pg.LegendItem(offset=(0, 1))
    legend.addItem(curves[i][0], "Output")
    legend.addItem(curves[i][1], "Current Phase Shift")
    legend.addItem(curves[i][2], "Phase Control")
    legend.addItem(curves[i][3], "Test Signal")
    legend.setParentItem(plotAreas[i])

# Time counter
t = 0
tick = 1 / sample_rate

# Decimation for the display to speed up computation
display_decimation = 10
frame_counter = 0

# Create loop timer
timer = QtCore.QTimer()


def update():
    global timer, curves, plotAreas, t, tick, frame_counter, duration, \
        PLLs, test_signals, phase_weight_matrix, connectivity_matrix

    # Stop the simulation when the duration has completed
    if t >= duration:
        timer.stop()

    # Update the test signal and the ppl (iterate simulation)
    for _i in range(0, number_of_PLLs):
        PLLs[_i].update(t, test_signals[_i].update(t), PLLs, _i, phase_weight_matrix, connectivity_matrix)
    # Update internal states for next iteration
    # (done separately from previous call to maintain consistent internal state across all iterations)
    for _i in range(0, number_of_PLLs):
        PLLs[_i].apply_next_phase_shift()

    # Graph the PLL states according to the display decimation
    if frame_counter % display_decimation == 0:
        for _i in range(0, number_of_PLLs):
            curves[_i][0].setData(PLLs[_i].output_log)
            curves[_i][2].setData(PLLs[_i].control_log)
            curves[_i][3].setData(test_signals[_i].signal_log)
            curves[_i][1].setData([x*100 for x in PLLs[_i].current_phase_shift_log])

    # Iterate the time counter according to the sample rate
    t += tick
    # Iterate the display frame counter
    frame_counter += 1

# Begin Simulation
timer.timeout.connect(update)
timer.start(0)

# # Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
