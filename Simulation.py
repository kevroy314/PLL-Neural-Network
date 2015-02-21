__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'  # TODO - Needs review for UI load/hang time, UI config, and IO

from pyqtgraph.Qt import QtGui, QtCore  # For GUI
import pyqtgraph as pg  # For GUI

from PIL import Image

from lib.visualization.LinePlotVisualizer import LinePlotVisualizer
from lib.visualization.GraphVisualizer import GraphVisualizer
from lib.visualization.TwoDVisualizer import TwoDVisualizer
from lib.app_modules.ConfigurationWindow import ConfigurationWindow
from lib.utils.HelperFunctions import *
from lib.PLLs.PLL_Network import ComplexPllNetwork


"""
Initialize the Simulation
"""
input_dir = r"C:\Users\Kevin\Desktop\School" + '\\'
input_file = "data.csv"

paused = True
duration = 9890
begin_integration_time = 0

connectivity_matrix = [[0, 0.08432127958685515, 0.08432127958685515, 0.11924829718838416, 0.1885481131059735, 0.1686425591737103, 0.266647298714324, 0.25296383876056544, 0.7988331750333647, 0.8831544546202198, 0.8032711371168835, 0.887170710126694, 0.8991118414747947, 0.8164402943868858, 0.9186688709410041, 0.837929081279775],
                       [0.08432127958685515, 0, 0.11924829718838416, 0.08432127958685515, 0.1686425591737103, 0.1885481131059735, 0.25296383876056544, 0.266647298714324, 0.8831544546202198, 0.9674757342070749, 0.887170710126694, 0.971143333638595, 0.9820639536426216, 0.8991118414747947, 1, 0.9186688709410041],
                       [0.08432127958685515, 0.11924829718838416, 0, 0.08432127958685515, 0.11924829718838416, 0.08432127958685515, 0.1885481131059735, 0.16864255917371027, 0.8032711371168835, 0.887170710126694, 0.7988331750333647, 0.8831544546202198, 0.887170710126694, 0.8032711371168835, 0.8991118414747947, 0.8164402943868858],
                       [0.11924829718838416, 0.08432127958685515, 0.08432127958685515, 0, 0.08432127958685515, 0.11924829718838416, 0.16864255917371027, 0.1885481131059735, 0.887170710126694, 0.971143333638595, 0.8831544546202198, 0.9674757342070749, 0.971143333638595, 0.887170710126694, 0.9820639536426216, 0.8991118414747947],
                       [0.1885481131059735, 0.1686425591737103, 0.11924829718838416, 0.08432127958685515, 0, 0.08432127958685515, 0.08432127958685513, 0.11924829718838414, 0.8991118414747947, 0.9820639536426216, 0.887170710126694, 0.971143333638595, 0.9674757342070749, 0.8831544546202198, 0.971143333638595, 0.887170710126694],
                       [0.1686425591737103, 0.1885481131059735, 0.08432127958685515, 0.11924829718838416, 0.08432127958685515, 0, 0.11924829718838414, 0.08432127958685513, 0.8164402943868858, 0.8991118414747947, 0.8032711371168835, 0.887170710126694, 0.8831544546202198, 0.7988331750333647, 0.887170710126694, 0.8032711371168835],
                       [0.266647298714324, 0.25296383876056544, 0.1885481131059735, 0.16864255917371027, 0.08432127958685513, 0.11924829718838414, 0, 0.08432127958685515, 0.9186688709410041, 1, 0.8991118414747947, 0.9820639536426216, 0.971143333638595, 0.887170710126694, 0.9674757342070749, 0.8831544546202198],
                       [0.25296383876056544, 0.266647298714324, 0.16864255917371027, 0.1885481131059735, 0.11924829718838414, 0.08432127958685513, 0.08432127958685515, 0, 0.837929081279775, 0.9186688709410041, 0.8164402943868858, 0.8991118414747947, 0.887170710126694, 0.8032711371168835, 0.8831544546202198, 0.7988331750333647],
                       [0.7988331750333647, 0.8831544546202198, 0.8032711371168835, 0.887170710126694, 0.8991118414747947, 0.8164402943868858, 0.9186688709410041, 0.837929081279775, 0, 0.08432127958685509, 0.08432127958685515, 0.11924829718838413, 0.18854811310597347, 0.1686425591737103, 0.26664729871432397, 0.25296383876056544],
                       [0.8831544546202198, 0.9674757342070749, 0.887170710126694, 0.971143333638595, 0.9820639536426216, 0.8991118414747947, 1, 0.9186688709410041, 0.08432127958685509, 0, 0.11924829718838413, 0.08432127958685515, 0.1686425591737103, 0.18854811310597347, 0.25296383876056544, 0.26664729871432397],
                       [0.8032711371168835, 0.887170710126694, 0.7988331750333647, 0.8831544546202198, 0.887170710126694, 0.8032711371168835, 0.8991118414747947, 0.8164402943868858, 0.08432127958685515, 0.11924829718838413, 0, 0.08432127958685509, 0.11924829718838413, 0.08432127958685515, 0.18854811310597347, 0.16864255917371027],
                       [0.887170710126694, 0.971143333638595, 0.8831544546202198, 0.9674757342070749, 0.971143333638595, 0.887170710126694, 0.9820639536426216, 0.8991118414747947, 0.11924829718838413, 0.08432127958685515, 0.08432127958685509, 0, 0.08432127958685515, 0.11924829718838413, 0.16864255917371027, 0.18854811310597347],
                       [0.8991118414747947, 0.9820639536426216, 0.887170710126694, 0.971143333638595, 0.9674757342070749, 0.8831544546202198, 0.971143333638595, 0.887170710126694, 0.18854811310597347, 0.1686425591737103, 0.11924829718838413, 0.08432127958685515, 0, 0.08432127958685509, 0.08432127958685513, 0.1192482971883841],
                       [0.8164402943868858, 0.8991118414747947, 0.8032711371168835, 0.887170710126694, 0.8831544546202198, 0.7988331750333647, 0.887170710126694, 0.8032711371168835, 0.1686425591737103, 0.18854811310597347, 0.08432127958685515, 0.11924829718838413, 0.08432127958685509, 0, 0.1192482971883841, 0.08432127958685513],
                       [0.9186688709410041, 1, 0.8991118414747947, 0.9820639536426216, 0.971143333638595, 0.887170710126694, 0.9674757342070749, 0.8831544546202198, 0.26664729871432397, 0.25296383876056544, 0.18854811310597347, 0.16864255917371027, 0.08432127958685513, 0.1192482971883841, 0, 0.08432127958685509],
                       [0.837929081279775, 0.9186688709410041, 0.8164402943868858, 0.8991118414747947, 0.887170710126694, 0.8032711371168835, 0.8831544546202198, 0.7988331750333647, 0.25296383876056544, 0.26664729871432397, 0.16864255917371027, 0.18854811310597347, 0.1192482971883841, 0.08432127958685513, 0.08432127958685509, 0]]

sim = ComplexPllNetwork(number_of_plls=16, sample_rate=400.0,
                        carrier_frequency=1.0, lowpass_cutoff_frequency=0.001,
                        connectivity_matrix=connectivity_matrix,
                        filter_order=3, filter_window_size=100,
                        in_signals_filename=input_dir + input_file)

"""
Initialize the GUI
"""

# Renderer Properties
render_video = False

# Set up application window
app = QtGui.QApplication([])
pg.setConfigOptions(antialias=True)

config_win = ConfigurationWindow(1, pause)

render_width = 1

graph = GraphVisualizer(2, [(255, 255, 255)], ["PLL 0 Phase", "PLL 0 Input Voltage"])
data0 = []
data1 = []

twod = TwoDVisualizer(int(render_width), int(sim.number_of_PLLs / render_width), "Real Phase Image")
twodimag = TwoDVisualizer(int(render_width), int(sim.number_of_PLLs / render_width), "Imaginary Phase Image")
phaseplot = LinePlotVisualizer(sim.number_of_PLLs, window_title="Phase Plot", distance=4.7625370521)
phasexa = []
phaseya = []
phaseza = []
for i in range(phaseplot.numLines):
    phasexa.append([])
    phaseya.append([])
    phaseza.append([])

lnint = LineIntegral(sim.number_of_PLLs)
ApEn = ApproximateEntropy(sim.number_of_PLLs, 2, 0.1)

phase_file = open(input_dir + 'phase_file_out.csv', 'w')
voltage_file = open(input_dir + 'voltage_file_out.csv', 'w')

display_decimation = config_win.display_decimation
frame_counter = 0

# Create loop timer
timer = QtCore.QTimer()

"""
Define Simulation Loop
"""


def update():
    global timer, twod, config_win, frame_counter, duration, paused, display_decimation, \
        phaseplot, phasexa, phaseya, phaseza, graph, data0, data1, lnint, ApEn
    paused, display_decimation = config_win.update(frame_counter)
    if not paused:
        # Stop the simulation when the duration has completed
        if sim.t >= duration:
            phase_file.close()
            voltage_file.close()
            print lnint.getTotal()
            print ApEn.getTotal(0)
            print ApEn.getTotal(1)
            timer.stop()

        sim.update()

        # Graph the PLL states according to the display decimation
        if frame_counter % display_decimation == 0:
            integral_data = []
            phase_line = ""
            voltage_line = ""
            for _i in range(sim.number_of_PLLs):
                phase_line = phase_line + str(sim.PLLs[_i].v(sim.PLLs[_i].next_phase_shift).real) + ","
                voltage_line = voltage_line + str(sim.PLLs[_i].previous_voltage.real) + ","
            for _i in range(phaseplot.numLines):
                tpl = (sim.PLLs[_i].v(sim.PLLs[_i].next_phase_shift).real, sim.PLLs[_i].previous_voltage.real, 0)
                phasexa[_i].append(tpl[0])
                phaseya[_i].append(tpl[1])
                phaseza[_i].append(tpl[2])
                integral_data.append(tpl)
            if sim.t - sim.tick < begin_integration_time <= sim.t:
                print "Beginning Integration."
            if sim.t >= begin_integration_time:
                phase_file.write(phase_line[0:-1] + "\n")
                voltage_file.write(voltage_line[0:-1] + "\n")
                lnint.update(integral_data)
                ApEn.update(integral_data)
            phaseplot.update(phasexa, phaseya, phaseza)
            data0.append(sim.PLLs[0].v(sim.PLLs[0].next_phase_shift).real)
            data1.append(sim.last_input[0])
            graph.update([data0, data1])
            image_data = array(np.zeros((sim.number_of_PLLs / render_width, render_width)), dtype=complex)
            for _i in range(0, sim.number_of_PLLs):
                row = np.floor(_i / render_width)
                col = _i % render_width
                image_data[row][col] = sim.PLLs[_i].v(sim.PLLs[_i].next_phase_shift)
            img_rotated = np.rot90(image_data, 3)
            twod.update(img_rotated.real, auto_levels=True)
            twodimag.update(img_rotated.imag, auto_levels=True)
            if render_video:
                # r, g, and b are 512x512 float arrays with values >= 0 and < 1.
                rgb_array = np.zeros((sim.number_of_PLLs / render_width, render_width, 3), 'uint8')
                rgb_array[..., 0] = image_data.real * 255
                rgb_array[..., 1] = 0
                rgb_array[..., 2] = image_data.imag * 255
                img = Image.fromarray(rgb_array)
                img.save('.\\video\\img_' + str(frame_counter).zfill(5) + '.png')
                realexporter = pg.exporters.ImageExporter.ImageExporter(twod.img)  # Ignore unresolved exporters ref
                imagexporter = pg.exporters.ImageExporter.ImageExporter(twodimag.img)  # Ignore unresolved exporters ref

                # set export parameters if needed
                realexporter.parameters()['width'] = int(render_width)  # (note this also affects height parameter)
                realexporter.parameters()['height'] = int(
                    sim.number_of_PLLs / render_width)  # (note this also affects height parameter)
                imagexporter.parameters()['width'] = int(render_width)  # (note this also affects height parameter)
                imagexporter.parameters()['height'] = int(
                    sim.number_of_PLLs / render_width)  # (note this also affects height parameter)
                realexporter.export('.\\video\\real\\img_' + str(frame_counter).zfill(5) + '.png')
                imagexporter.export('.\\video\\imaginary\\img_' + str(frame_counter).zfill(5) + '.png')

        # Iterate the display frame counter
        frame_counter += 1


"""
Begin the Simulation and GUI
"""


# Begin Simulation
# noinspection PyUnresolvedReferences
timer.timeout.connect(update)
timer.start(0)

# # Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        # noinspection PyArgumentList
        QtGui.QApplication.instance().exec_()