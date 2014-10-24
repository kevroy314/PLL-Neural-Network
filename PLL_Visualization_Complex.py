'''
TODO:
-Add input sources from image files (bmps)
'''

__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

from pyqtgraph.Qt import QtGui, QtCore  # For GUI
import pyqtgraph as pg  # For GUI
from PIL import Image
from PLL_Complex import PLL_Complex
from TwoDVisualizer import TwoDVisualizer
from ConfigurationWindow import ConfigurationWindow
from TestSignals import ComplexSineSignal
from HelperFunctions import *
import os

"""
Initialize the Simulation
"""

# Renderer Properties
render_video = True

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

# Make the connectivity matrix fully connected
connectivity_matrix = array(np.ones([number_of_PLLs, number_of_PLLs]), dtype=complex)

for _i in range(0, number_of_PLLs):
    for _j in range(0, number_of_PLLs):
        _sum = float(0)
        for _k in range(0, len(keys)):
            ki = complex(float(keys[_k][_i][0])/255, float(keys[_k][_i][2])/255)
            kj = complex(float(keys[_k][_j][0])/255, float(-keys[_k][_j][2])/255)  # conjugate
            _sum += ki * kj
        connectivity_matrix[_i][_j] = _sum / number_of_PLLs
print "Real Part"
print_padded_matrix(connectivity_matrix.real)
print "Imag Part"
print_padded_matrix(connectivity_matrix.imag)

# Validate Weight Matrix Symmetry
if (np.array(phase_weight_matrix).transpose() != np.array(phase_weight_matrix)).any():
    print "Error: Phase Offset Matrix Not Symmetric Across Diagonal."
else:
    print "Array Symmetry Validated."

# Create PLLs
for i in range(0, number_of_PLLs):
    PLLs.append(PLL_Complex(sample_rate, carrier_frequency, lowpass_cutoff_frequency, 1.57079))

input_signals = np.zeros(number_of_PLLs)

# Create Test Signals
for i in range(0, number_of_PLLs):
    test_signals.append(ComplexSineSignal(1, carrier_frequency, input_signals[i], noise_level=noise_level))


"""
Initialize the GUI
"""

# Set up application window
app = QtGui.QApplication([])
pg.setConfigOptions(antialias=True)

config_win = ConfigurationWindow(1)

twod = TwoDVisualizer(int(render_width), int(number_of_PLLs/render_width))
twodimag = TwoDVisualizer(int(render_width), int(number_of_PLLs/render_width))

display_decimation = config_win.display_decimation
frame_counter = 0

# Create loop timer
timer = QtCore.QTimer()

"""
Define Simulation Loop
"""


def update():
    global timer, twod, config_win, t, tick, frame_counter, duration, \
        PLLs, test_signals, phase_weight_matrix, connectivity_matrix, paused, display_decimation
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
            image_data = array(np.zeros((number_of_PLLs/render_width, render_width)), dtype=complex)
            for _i in range(0, number_of_PLLs):
                    row = np.floor(_i / render_width)
                    col = _i % render_width
                    image_data[row][col] = PLLs[_i].v(PLLs[_i].applied_phase_shift_log[-1])
            img_rotated = np.rot90(image_data, 3)
            twod.update(img_rotated.real, autoLevels=True)
            twodimag.update(img_rotated.imag, autoLevels=True)
            if render_video:
                # r, g, and b are 512x512 float arrays with values >= 0 and < 1.
                rgbArray = np.zeros((number_of_PLLs/render_width, render_width, 3), 'uint8')
                rgbArray[..., 0] = image_data.real * 255
                rgbArray[..., 1] = 0
                rgbArray[..., 2] = image_data.imag * 255
                img = Image.fromarray(rgbArray)
                img.save('.\Images\img_' + str(frame_counter).zfill(5) + '.png')
                realexporter = pg.exporters.ImageExporter.ImageExporter(twod.img)
                imagexporter = pg.exporters.ImageExporter.ImageExporter(twodimag.img)

                # set export parameters if needed
                realexporter.parameters()['width'] = int(render_width)  # (note this also affects height parameter)
                realexporter.parameters()['height'] = int(number_of_PLLs/render_width)  # (note this also affects height parameter)
                imagexporter.parameters()['width'] = int(render_width)  # (note this also affects height parameter)
                imagexporter.parameters()['height'] = int(number_of_PLLs/render_width)  # (note this also affects height parameter)
                realexporter.export('.\Real Images\img_' + str(frame_counter).zfill(5) + '.png')
                imagexporter.export('.\Imaginary Images\img_' + str(frame_counter).zfill(5) + '.png')
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