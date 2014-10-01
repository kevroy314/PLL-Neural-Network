__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

from pyqtgraph.Qt import QtGui, QtCore  # For GUI
import pyqtgraph as pg  # For GUI
from pylab import *  # For PLL
from PLL import PLL
from TestSignals import SineSignal
import pickle

"""
Initialize the Simulation
"""

# Renderer Properties
render_video = False

# Simulation Properties
sample_rate = 10000.0
carrier_frequency = 2
lowpass_cutoff_frequency = 0.5  # Must be <= carrier_frequency/2
number_of_PLLs = 10
paused = False

t = 0
tick = 1 / sample_rate
PLLs = []

# Test Signal Properties
noise_level = 0.0
duration = 1

test_signals = []

# Training Configuration
lock_feedback_signal = False  # Set to false for no training
feedback_signal_lock_profile = np.ones(number_of_PLLs)
for i in range(0, number_of_PLLs):  # Set lock profile
    if i == 0:
        feedback_signal_lock_profile[i] *= 2*pi
    if i == 1:
        feedback_signal_lock_profile[i] *= 4*pi
    if i == 2:
        feedback_signal_lock_profile[i] *= 8*pi
    if i == 3:
        feedback_signal_lock_profile[i] *= 16*pi
    if i == 4:
        feedback_signal_lock_profile[i] *= 1
    if i == 5:
        feedback_signal_lock_profile[i] *= 1
    if i == 6:
        feedback_signal_lock_profile[i] *= 1
    if i == 7:
        feedback_signal_lock_profile[i] *= 1
    if i == 8:
        feedback_signal_lock_profile[i] *= 1
    if i == 9:
        feedback_signal_lock_profile[i] *= 1
    #else:
        #feedback_signal_lock_profile[i] *= 1
    #feedback_signal_lock_profile[i] *= (i % 2) + 1

# Generate a random symmetric phase weight matrix
phase_weight_matrix = np.random.randn(number_of_PLLs, number_of_PLLs)
phase_weight_matrix += np.array(phase_weight_matrix).transpose()
phase_weight_matrix /= 2


# Print the weight matrix in a readable way
def print_padded_matrix(in_matrix):
    col_width = max(len(word.astype('|S10')) for row in in_matrix for word in row) + 2  # Padding
    for row in in_matrix:
        print "".join(word.astype('|S10').ljust(col_width) for word in row)

print_padded_matrix(phase_weight_matrix)

# Make the connectivity matrix fully connected
connectivity_matrix = np.ones([number_of_PLLs, number_of_PLLs])

# Validate Weight Matrix Symmetry
if (np.array(phase_weight_matrix).transpose() != np.array(phase_weight_matrix)).any():
    print "Error: Phase Offset Matrix Not Symmetric Across Diagonal."
else:
    print "Array Symmetry Validated."

# Create PLLs
for i in range(0, number_of_PLLs):
    PLLs.append(PLL(sample_rate, carrier_frequency, lowpass_cutoff_frequency, 1.57079))

# Create Test Signals
for i in range(0, number_of_PLLs):
    test_signals.append(SineSignal(1, carrier_frequency, 0, noise_level=noise_level))

# Lock Feedback Signal (if specified)
if lock_feedback_signal:
    for i in range(0, number_of_PLLs):
        PLLs[i].set_feedback_signal_lock(True, feedback_signal_lock_profile[i])

"""
Initialize the GUI
"""


# Set up application window
app = QtGui.QApplication([])
win = pg.GraphicsWindow(title="PLL Example Animated")
win.resize(1000, 600)
win.setWindowTitle('PLL State Graphs')

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
    legend.addItem(curves[i][0], "Input Signal")
    legend.addItem(curves[i][1], "Detected Phase")
    legend.addItem(curves[i][2], "Current Phase Shift")
    legend.addItem(curves[i][3], "Output Voltage")
    legend.setParentItem(plotAreas[i])

img_win = pg.GraphicsWindow(title="PLL Example Animated")
img_win.resize(300, 300)
img_win.setWindowTitle('PLL Example Phase Image')

img = pg.ImageItem(autoLevels=False, levels=(-2.0, 2.0))
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

lockFeedbackBtn = QtGui.QPushButton("Lock Feedback", config_win)


def lock_feedback():
    global lock_feedback_signal, lockFeedbackBtn
    lock_feedback_signal = not lock_feedback_signal
    if lock_feedback_signal:
        for _i in range(0, number_of_PLLs):
            PLLs[_i].set_feedback_signal_lock(True, feedback_signal_lock_profile[_i])
        lockFeedbackBtn.setText("Unlock Feedback")
    else:
        for _i in range(0, number_of_PLLs):
            PLLs[_i].set_feedback_signal_lock(False, feedback_signal_lock_profile[_i])
        lockFeedbackBtn.setText("Lock Feedback")


lockFeedbackBtn.clicked.connect(lock_feedback)
l.addWidget(lockFeedbackBtn, 3, 0)

saveLockProfileBtn = QtGui.QPushButton("Save Lock Profile", config_win)


def save_lock_profile():
    global feedback_signal_lock_profile, saveLockProfileBtn
    filename = QtGui.QFileDialog.getSaveFileName(saveLockProfileBtn, "Save Lock Profile", "", "*.signal.lock")
    if filename != "":
        file_object = open(filename, 'w')
        pickle.dump(feedback_signal_lock_profile, file_object)
        print feedback_signal_lock_profile


saveLockProfileBtn.clicked.connect(save_lock_profile)
l.addWidget(saveLockProfileBtn, 4, 0)

loadLockProfileBtn = QtGui.QPushButton("Load Lock Profile", config_win)


def load_lock_profile():
    global feedback_signal_lock_profile, loadLockProfileBtn
    filename = QtGui.QFileDialog.getOpenFileName(loadLockProfileBtn, "Load Lock Profile", "", "*.signal.lock")
    if filename != "":
        file_object = open(filename, 'r')
        feedback_signal_lock_profile = pickle.load(file_object)
        print feedback_signal_lock_profile


loadLockProfileBtn.clicked.connect(load_lock_profile)
l.addWidget(loadLockProfileBtn, 5, 0)

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

# Create loop timer
timer = QtCore.QTimer()

"""
Define Simulation Loop
"""


def update():
    global timer, curves, plotAreas, img, t, tick, frame_counter, duration, \
        PLLs, test_signals, phase_weight_matrix, connectivity_matrix

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
            for _i in range(0, number_of_PLLs):
                curves[_i][0].setData([x for x in test_signals[_i].signal_log])
                curves[_i][1].setData([x for x in PLLs[_i].detected_phase_log])
                curves[_i][2].setData([x for x in PLLs[_i].applied_phase_shift_log])
                curves[_i][3].setData([x for x in PLLs[_i].output_voltage_log])
            image_data = np.zeros((number_of_PLLs, number_of_PLLs))
            pos = 0
            for _i in range(0, number_of_PLLs):
                for _j in range(_i+1, number_of_PLLs):
                    row = pos%8
                    col = np.floor(pos/8)
                    image_data[row][col] = PLLs[_i].v(PLLs[_i].applied_phase_shift_log[-1]) * \
                                        PLLs[_j].v(PLLs[_j].applied_phase_shift_log[-1])
                    pos += 1
            print pos
            img.setImage(image_data, autoLevels=False)
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


