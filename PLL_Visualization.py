__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

from pyqtgraph.Qt import QtGui, QtCore  # For GUI
import pyqtgraph as pg  # For GUI
from pylab import *  # For PLL
from PLL import PLL
from TestSignals import SineSignal


"""
Initialize the Simulation
"""


# Simulation Properties
sample_rate = 40000.0
carrier_frequency = 200
lowpass_cutoff_frequency = 5
t = 0
tick = 1 / sample_rate

number_of_PLLs = 10
PLLs = []

phase_weight_matrix = [
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
]

connectivity_matrix = np.ones([number_of_PLLs, number_of_PLLs])

# Validate Weight Matrix
if (np.array(phase_weight_matrix).transpose() != np.array(phase_weight_matrix)).any():
    print "Error: Phase Offset Matrix Not Symmetric Across Diagonal."
else:
    print "Array Symmetry Validated."

# Test Signal Properties
noise_level = 0
duration = 4
test_signals = []


# Create PLL
for i in range(0, number_of_PLLs):
    PLLs.append(PLL(sample_rate, carrier_frequency, lowpass_cutoff_frequency, 1, -1.57079))

# Create Test Signals
for i in range(0, number_of_PLLs):
    test_signals.append(SineSignal(1, carrier_frequency, i, noise_level))


"""
Initialize the GUI
"""


# Set up application window
app = QtGui.QApplication([])
win = pg.GraphicsWindow(title="PLL Example Animated")
win.resize(1000, 600)
win.setWindowTitle('PLL Example Animated')

img_win = pg.GraphicsWindow(title="PLL Example Animated")
img_win.resize(300, 300)
img_win.setWindowTitle('PLL Example Phase Image')

pg.setConfigOptions(antialias=True)

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

img = pg.ImageItem()
w = pg.GradientWidget()
w.setTickColor(0, QtGui.QColor(255, 69, 00))
w.setTickColor(1, QtGui.QColor(0, 0, 128))
lut = w.getLookupTable(65536)
img.setLookupTable(lut, update=True)
data = np.random.randn(number_of_PLLs, number_of_PLLs)
img.setImage(data)
img_view = img_win.addViewBox()
img_view.addItem(img)

# Decimation for the display to speed up computation
display_decimation = 10
frame_counter = 0

# Create loop timer
timer = QtCore.QTimer()


"""
Define Simulation Loop
"""


def update():
    global timer, curves, plotAreas, img, t, tick, frame_counter, duration, \
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
            curves[_i][0].setData([x*1 for x in PLLs[_i].output_log])
            curves[_i][1].setData([x*1 for x in PLLs[_i].current_phase_shift_log])
            curves[_i][2].setData([x*1 for x in PLLs[_i].control_log])
            curves[_i][3].setData([x*1 for x in test_signals[_i].signal_log])
        image_data = np.zeros((number_of_PLLs, number_of_PLLs))
        for _i in range(0, number_of_PLLs):
            for _j in range(0, number_of_PLLs):
                image_data[_i][_j] = PLLs[_i].current_phase_shift - PLLs[_j].current_phase_shift
        img.setImage(image_data)
    # Iterate the time counter according to the sample rate
    t += tick
    # Iterate the display frame counter
    frame_counter += 1


"""
Begin the Simulation and GUI
"""


# Begin Simulation
timer.timeout.connect(update)
timer.start(0)

# # Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
