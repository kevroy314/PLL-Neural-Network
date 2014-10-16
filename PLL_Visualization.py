'''
TODO:
-Add input sources from image files (bmps)
'''

__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

from pyqtgraph.Qt import QtGui, QtCore  # For GUI
import pyqtgraph as pg  # For GUI
from pylab import *  # For PLL
from PLL import PLL
from ThreeDVisualizer import ThreeDVisualizer
from TestSignals import SineSignal
import pickle
import PIL
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

#phase_weight_matrix = np.random.randn(number_of_PLLs, number_of_PLLs)
#phase_weight_matrix += np.array(phase_weight_matrix).transpose()
#phase_weight_matrix /= 2
phase_weight_matrix = np.ones((number_of_PLLs, number_of_PLLs))


# Print the weight matrix in a readable way
def print_padded_matrix(in_matrix):
    col_width = max(len(word.astype('|S10')) for row in in_matrix for word in row) + 2  # Padding
    for row in in_matrix:
        print "".join(word.astype('|S10').ljust(col_width) for word in row)


def get_image_data_from_file(filename):
    _img = PIL.Image.open(filename)
    _bin_img = _img.convert("P")
    _data = list(_bin_img.getdata())
    _data_out = np.zeros((len(_data)))
    for _i in range(0, len(_data)):
        _data_out[_i] = _data[_i]
    return _data_out

keys = []

for _file in os.listdir(".\keys"):
    if _file.endswith(".bmp"):
        keys.append(get_image_data_from_file(".\keys\\"+_file))

'''key0 = np.array([[0, 1, 1, 1, 1, 0],
                 [0, 1, 0, 0, 1, 0],
                 [1, 1, 0, 0, 1, 1],
                 [1, 1, 0, 0, 1, 1],
                 [1, 0, 0, 0, 0, 1],
                 [1, 0, 0, 0, 0, 1],
                 [1, 1, 0, 0, 1, 1],
                 [1, 1, 0, 0, 1, 1],
                 [0, 1, 0, 0, 1, 0],
                 [0, 1, 1, 1, 1, 0]]).reshape(number_of_PLLs)

key1 = np.array([[0, 0, 1, 1, 0, 0],
                 [0, 1, 1, 1, 0, 0],
                 [1, 1, 1, 1, 0, 0],
                 [0, 0, 1, 1, 0, 0],
                 [0, 0, 1, 1, 0, 0],
                 [0, 0, 1, 1, 0, 0],
                 [0, 0, 1, 1, 0, 0],
                 [0, 0, 1, 1, 0, 0],
                 [0, 0, 1, 1, 0, 0],
                 [1, 1, 1, 1, 1, 1]]).reshape(number_of_PLLs)

key2 = np.array([[0, 1, 1, 1, 1, 0],
                 [1, 1, 1, 1, 1, 1],
                 [1, 1, 0, 0, 1, 1],
                 [0, 0, 0, 0, 1, 1],
                 [0, 0, 0, 0, 1, 1],
                 [0, 0, 0, 1, 1, 0],
                 [0, 0, 1, 1, 0, 0],
                 [0, 1, 1, 0, 0, 0],
                 [1, 1, 1, 1, 1, 1],
                 [1, 1, 1, 1, 1, 1]]).reshape(number_of_PLLs)

key0 = np.array([[0, 0, 0, 0, 0],
                 [0, 1, 0, 1, 0],
                 [0, 0, 0, 0, 0],
                 [1, 0, 0, 0, 1],
                 [0, 1, 1, 1, 0]]).reshape(number_of_PLLs)
'''

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
if enableGraphs:
    win = pg.GraphicsWindow(title="PLL Example Animated")
    win.resize(1000, 600)
    win.setWindowTitle('PLL State Graphs')

    pg.setConfigOptions(antialias=True)

    # Set up plot environment
    plotAreas = []
    curves = []
    for i in range(0, 5):
        plotAreas.append(win.addPlot())
        win.nextRow()
        plotAreas[i].enableAutoRange('xy', True)
        curves.append(
            [plotAreas[i].plot(pen=(255, 0, 0)), plotAreas[i].plot(pen=(0, 255, 0)), plotAreas[i].plot(pen=(0, 0, 255)),
             plotAreas[i].plot(pen=(255, 255, 255))])

        legend = pg.LegendItem(offset=(0, 1))
        legend.addItem(curves[i][0], "Input Signal")
        legend.addItem(curves[i][1], "Detected Phase")
        legend.addItem(curves[i][2], "Current Phase Shift")
        legend.addItem(curves[i][3], "Output Voltage")
        legend.setParentItem(plotAreas[i])

img_win = pg.GraphicsWindow(title="PLL Example Animated")
img_win.resize(300, 300)
img_win.setWindowTitle('PLL Example Phase Image')

img = pg.ImageItem(autoLevels=False, levels=(-0.1, 0.1))
w = pg.GradientWidget()
w.setTickColor(0, QtGui.QColor(255, 69, 00))
w.setTickColor(1, QtGui.QColor(0, 0, 128))
lut = w.getLookupTable(65536)
img.setLookupTable(lut, update=False)
data = np.random.randn(number_of_PLLs, number_of_PLLs)
img.setImage(data)
img_view = img_win.addViewBox()
img_view.addItem(img)

config_win = QtGui.QMainWindow()
config_win.resize(300, 200)
config_win.show()
config_win.setWindowTitle('Configuration')
cw = QtGui.QWidget()
config_win.setCentralWidget(cw)

l = QtGui.QGridLayout()
cw.setLayout(l)
l.setSpacing(0)

pauseBtn = QtGui.QPushButton("Pause", config_win)


def pause():
    global paused, pauseBtn
    paused = not paused
    display_text = "Pause"
    if paused:
        display_text = "Continue"
    pauseBtn.setText(display_text)


pauseBtn.clicked.connect(pause)
l.addWidget(pauseBtn, 0, 0)

saveWeightMatrixBtn = QtGui.QPushButton("Save Weight Matrix", config_win)


def save_weight_matrix():
    global phase_weight_matrix, saveWeightMatrixBtn
    filename = QtGui.QFileDialog.getSaveFileName(saveWeightMatrixBtn, "Save Weight Matrix", "", "*.phases")
    if filename != "":
        file_object = open(filename, 'w')
        pickle.dump(phase_weight_matrix, file_object)
        print_padded_matrix(phase_weight_matrix)


saveWeightMatrixBtn.clicked.connect(save_weight_matrix)
l.addWidget(saveWeightMatrixBtn, 1, 0)

loadWeightMatrixBtn = QtGui.QPushButton("Load Weight Matrix", config_win)


def load_weight_matrix():
    global phase_weight_matrix, loadWeightMatrixBtn
    filename = QtGui.QFileDialog.getOpenFileName(loadWeightMatrixBtn, "Load Weight Matrix", "", "*.phases")
    if filename != "":
        file_object = open(filename, 'r')
        phase_weight_matrix = pickle.load(file_object)
        print_padded_matrix(phase_weight_matrix)


loadWeightMatrixBtn.clicked.connect(load_weight_matrix)
l.addWidget(loadWeightMatrixBtn, 2, 0)

# Decimation for the display to speed up computation
if render_video:
    display_decimation = 1
else:
    display_decimation = 10


def decimation_value_changed(sb):
    global display_decimation
    display_decimation = sb.value()

decimationLabel = QtGui.QLabel("Display Decimation, min=0, no maximum.")
decimationSpinBox = pg.SpinBox(value=display_decimation, bounds=[1, None], step=1)
l.addWidget(decimationLabel, 6, 0)
l.addWidget(decimationSpinBox, 7, 0)
decimationSpinBox.sigValueChanged.connect(decimation_value_changed)

if render_video:
    # create an exporter instance, as an argument give it
    # the item you wish to export
    exporter = pg.exporters.ImageExporter.ImageExporter(img)

    # set export parameters if needed
    exporter.parameters()['width'] = img_win.width()  # (note this also affects height parameter)

frame_counter = 0


# 3D Test

## precompute height values for all frames
threed = ThreeDVisualizer(render_width, number_of_PLLs/render_width)
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
    global timer, curves, plotAreas, img, t, tick, frame_counter, duration, \
        PLLs, test_signals, phase_weight_matrix, connectivity_matrix, index, z
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
                for _i in range(0, 5):
                    curves[_i][0].setData([x for x in test_signals[_i].signal_log])
                    curves[_i][1].setData([x for x in PLLs[_i].detected_phase_log])
                    curves[_i][2].setData([x for x in PLLs[_i].applied_phase_shift_log])
                    curves[_i][3].setData([x for x in PLLs[_i].output_voltage_log])
            image_data = np.zeros((number_of_PLLs/render_width, render_width))
            for _i in range(0, number_of_PLLs):
                    row = np.floor(_i / render_width)
                    col = _i % render_width
                    image_data[row][col] = PLLs[_i].v(PLLs[_i].applied_phase_shift_log[-1])# * \
                                           #PLLs[0].v(PLLs[0].applied_phase_shift_log[-1])
            img.setImage(np.rot90(image_data, 3), autoLevels=True)
            timage_data = np.zeros((render_width, number_of_PLLs/render_width, 4))
            timage_data[:, :, 0] = np.rot90(image_data, 3)
            threed.update(timage_data, z[index])
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