__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

from pyqtgraph.Qt import QtGui, QtCore  # For GUI
import pyqtgraph as pg  # For GUI
from lib.PLLs.PLL import PLL
from lib.visualization.TwoDVisualizer import TwoDVisualizer
from lib.visualization.GraphVisualizer import GraphVisualizer
from lib.app_modules.ConfigurationWindow import ConfigurationWindow
from lib.app_modules.HelperFunctions import *
from lib.signals.TestSignals import SineSignal
import os

"""
Initialize the Simulation
"""

# Renderer Properties
render_video = False  # Save images for each frame of 2D visualizer
enableGraphs = True  # Show graphs (slows performance) of primary simulation variables

# Simulation Properties
sample_rate = 10000.0  # S/s
carrier_frequency = 2  # Hz
lowpass_cutoff_frequency = 1  # Must be <= carrier_frequency/2
number_of_PLLs = 60  # Must be number of pixels in important keys
render_width = 6  # Must be multiple of # of PLLs
paused = False

t = 0  # Simulation time
tick = 1 / sample_rate  # Simulation tick
PLLs = []  # Stores PLL Objects
test_signals = []  # Store input signals

# Test Signal Properties
noise_level = 0.1  # Deviation from standard sine via random normals
duration = 10  # Simulation will stop automatically after t>duration

"""
Load Keys from File for Training
"""

keys = []

for _file in os.listdir(".\\input\\keys"):
    if _file.endswith(".bmp"):
        keys.append(get_image_data_from_file(".\\input\\keys\\"+_file))

# Make the connectivity matrix fully connected
connectivity_matrix = np.ones([number_of_PLLs, number_of_PLLs])

for _i in range(0, number_of_PLLs):
    for _j in range(0, number_of_PLLs):
        _sum = float(0)
        for _k in range(0, len(keys)):
            _sum += keys[_k][_i] * keys[_k][_j]
        connectivity_matrix[_i][_j] = _sum / number_of_PLLs

print_padded_matrix(connectivity_matrix)

# Validate Weight Matrix Symmetry
if (np.array(connectivity_matrix).transpose() != np.array(connectivity_matrix)).any():
    print "Error: Phase Offset Matrix Not Symmetric Across Diagonal."
else:
    print "Array Symmetry Validated."

"""
Initialize Simulation Objects
"""

# Create PLLs
for i in range(0, number_of_PLLs):
    PLLs.append(PLL(sample_rate, carrier_frequency, lowpass_cutoff_frequency, 1.57079))

for _file in os.listdir(".\\input\\in_signals"):
    if _file.endswith(".bmp"):
        input_signals = get_image_data_from_file(".\\input\\in_signals\\"+_file)
        break

# Create Test Signals
for i in range(0, number_of_PLLs):
    test_signals.append(SineSignal(1, carrier_frequency, input_signals[i], noise_level=noise_level))


"""
Initialize the GUI
"""

# Set up application window
app = QtGui.QApplication([])
pg.setConfigOptions(antialias=True)

if enableGraphs:
    graph_vis = GraphVisualizer(5,
                                [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255)],
                                ["Input Signal", "Detected Phase", "Current Phase Shift", "Output Voltage"])

twod = TwoDVisualizer(int(render_width), int(number_of_PLLs/render_width))

display_decimation = 2
config_win = ConfigurationWindow(display_decimation)

if render_video:
    # create an exporter instance, as an argument give it
    # the item you wish to export
    exporter = pg.exporters.ImageExporter.ImageExporter(twod.img)

    # set export parameters if needed
    exporter.parameters()['width'] = render_width  # (note this also affects height parameter)

frame_counter = 0

# Create loop timer
timer = QtCore.QTimer()

"""
Define Simulation Loop
"""


def update():
    global timer, twod, graph_vis, config_win, t, tick, frame_counter, duration, \
        PLLs, test_signals, connectivity_matrix, paused, display_decimation
    paused, connectivity_matrix, display_decimation = config_win.update(connectivity_matrix)
    if not paused:
        # Stop the simulation when the duration has completed
        if t >= duration:
            timer.stop()

        # Update the test signal and the ppl (iterate simulation)
        for _i in range(0, number_of_PLLs):
            PLLs[_i].update(t, test_signals[_i].update(t), PLLs, _i, connectivity_matrix)
        # Update internal states for next iteration
        # (done separately from previous call to maintain consistent internal state across all iterations)
        for _i in range(0, number_of_PLLs):
            PLLs[_i].apply_next_phase_shift()

        # Graph the PLL states according to the display decimation
        if frame_counter % display_decimation == 0:
            if enableGraphs:
                data = []
                for _i in range(0, graph_vis.num_rows):
                    data.append([x for x in test_signals[_i].signal_log])
                    data.append([x for x in PLLs[_i].detected_phase_log])
                    data.append([x for x in PLLs[_i].applied_phase_shift_log])
                    data.append([x for x in PLLs[_i].output_voltage_log])
                graph_vis.update(data)
            image_data = np.zeros((number_of_PLLs/render_width, render_width))
            for _i in range(0, number_of_PLLs):
                    row = np.floor(_i / render_width)
                    col = _i % render_width
                    image_data[row][col] = PLLs[_i].v(PLLs[_i].applied_phase_shift_log[-1])
            img_rotated = np.rot90(image_data, 3)
            twod.update(img_rotated, autoLevels=True)
            if render_video:
                exporter.export('.\\video\\img_' + str(frame_counter).zfill(5) + '.png')
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