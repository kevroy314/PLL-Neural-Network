'''
TODO:
-Add input sources from image files (bmps)
'''

__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

from pyqtgraph.Qt import QtGui, QtCore  # For GUI
import pyqtgraph as pg  # For GUI
from PLL import PLL
from ThreeDVisualizer import ThreeDVisualizer
from TwoDVisualizer import TwoDVisualizer
from GraphVisualizer import GraphVisualizer
from ConfigurationWindow import ConfigurationWindow
from TestSignals import SineSignal
from HelperFunctions import *
import os

"""
Initialize the Simulation
"""

# Renderer Properties
render_video = False
enableGraphs = True

# Simulation Properties
sample_rate = 10000.0
carrier_frequency = 2
lowpass_cutoff_frequency = 1  # Must be <= carrier_frequency/2
number_of_PLLs = 60
render_width = 6
paused = False

t = 0
tick = 1 / sample_rate
PLLs = []

# Test Signal Properties
noise_level = 0.1
duration = 10

test_signals = []

phase_weight_matrix = np.ones((number_of_PLLs, number_of_PLLs))

keys = []

for _file in os.listdir(".\complex_keys"):
    if _file.endswith(".bmp"):
        keys.append(get_rgb_image_data_from_file(".\complex_keys\\"+_file))

# TODO MAKE CONNECTIVITY COMPLEX AND CHANGE TO COMPLEX LEARNING RULE

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
if (np.array(phase_weight_matrix).transpose() != np.array(phase_weight_matrix)).any():
    print "Error: Phase Offset Matrix Not Symmetric Across Diagonal."
else:
    print "Array Symmetry Validated."

# Create PLLs
for i in range(0, number_of_PLLs):
    PLLs.append(PLL(sample_rate, carrier_frequency, lowpass_cutoff_frequency, 1.57079))

input_signals = get_image_data_from_file("noised_1.bmp")

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

config_win = ConfigurationWindow()

twod = TwoDVisualizer(int(render_width), int(number_of_PLLs/render_width))

display_decimation = 10

if render_video:
    # Decimation for the display to speed up computation
    display_decimation = 1
    # create an exporter instance, as an argument give it
    # the item you wish to export
    exporter = pg.exporters.ImageExporter.ImageExporter(twod.img)

    # set export parameters if needed
    exporter.parameters()['width'] = render_width  # (note this also affects height parameter)

frame_counter = 0

## precompute height values for all frames
threed = ThreeDVisualizer(int(render_width), int(number_of_PLLs/render_width))
d = (threed.x ** 2 + threed.y ** 2) * 0.1
d2 = d ** 0.5 + 0.1
phi = np.arange(0, np.pi*2, np.pi/20.)
z = np.sin(d[np.newaxis, ...] + phi.reshape(phi.shape[0], 1, 1)) / d2[np.newaxis, ...]
index = 0


# Create loop timer
timer = QtCore.QTimer()

"""
Define Simulation Loop
"""


def update():
    global timer, twod, threed, graph_vis, config_win, t, tick, frame_counter, duration, \
        PLLs, test_signals, phase_weight_matrix, connectivity_matrix, index, paused, display_decimation
    paused, phase_weight_matrix, display_decimation = config_win.update(phase_weight_matrix)
    if not paused:
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
            timage_data = np.zeros((threed.width, threed.height, 4))
            timage_data[:, :, 0] = img_rotated
            timage_data[:, :, 1] = img_rotated
            timage_data[:, :, 2] = img_rotated
            timage_data[:, :, 3] = img_rotated
            threed.update(z, timage_data, index)
            index = (index+1) % len(z)
            if render_video:
                exporter.export('.\Images\img_' + str(frame_counter).zfill(5) + '.png')
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