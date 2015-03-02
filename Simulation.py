__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

from pyqtgraph.Qt import QtGui, QtCore  # For GUI
import pyqtgraph as pg  # For GUI

import datetime

from lib.visualization.LinePlotVisualizer import LinePlotVisualizer
from lib.visualization.GraphVisualizer import GraphVisualizer
from lib.app_modules.ConfigurationWindow import ConfigurationWindow
from lib.utils.HelperFunctions import *
from lib.PLLs.PLL_Network import PllNetwork


"""
Initialize the Simulation
"""
run_name = "euclidean_Connectivity"
input_dir = r"C:\Users\Kevin\Desktop\School" + '\\'
input_file = "data.npy"

paused = True
duration = 9890
begin_integration_time = 0
#connectivity_matrix = [[0.5] * 16] * 16


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


sim = PllNetwork(number_of_plls=16, sample_rate=400.0,
                 carrier_frequency=1, lowpass_cutoff_frequency=0.4,
                 connectivity_matrix=connectivity_matrix,
                 filter_order=3, filter_window_size=100,
                 in_signals_filename=input_dir + input_file)

# Output Configuration
save_raw_file = True
inline_apen = False
inline_path_length = False
inline_apen_window_size = 100
inline_path_length_window_size = 2

if save_raw_file:
    phase_line = ""
    voltage_line = ""
    time_string = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    phase_file = open(input_dir + 'phase_file_out_' + time_string + '_' + run_name + '.csv', 'w')
    voltage_file = open(input_dir + 'voltage_file_out_' + time_string + '_' + run_name + '.csv', 'w')

if inline_apen:
    ApEn = WindowedApproximateEntropyMeasure(sim.number_of_PLLs * 2, inline_apen_window_size, 2, 0.1)
    measures_data = []
if inline_path_length:
    path_length = WindowedPathLengthMeasure(sim.number_of_PLLs * 2, inline_path_length_window_size)
    measures_data = []

"""
Initialize the GUI
"""

# UI Element Properties
show_graphs = True
show_phase_plot = True
max_display_points_window = 250

# Set up application window
app = QtGui.QApplication([])
pg.setConfigOptions(antialias=True)


if show_graphs:
    num_graphs = 6
    graph = GraphVisualizer(num_graphs, [(255, 255, 255)],
                            ["PLL 0 Input", "PLL 0 Detected Phase", "PLL 0 Filtered Phase",
                             "PLL 0 Interactive Phase", "PLL 0 Phase Output", "PLL 0 Voltage Output"])
    data = []
    for i in range(0, num_graphs):
        data.append(deque([], max_display_points_window))

if show_phase_plot:
    phaseplot = LinePlotVisualizer(1, window_title="Phase Plot", distance=4.7625370521)
    phasexa = []
    phaseya = []
    phaseza = []
    for i in range(phaseplot.numLines):
        phasexa.append(deque([], max_display_points_window))
        phaseya.append(deque([], max_display_points_window))
        phaseza.append(deque([], max_display_points_window))

config_win = ConfigurationWindow(1, pause)

display_decimation = config_win.display_decimation
frame_counter = 0

# Create loop timer
timer = QtCore.QTimer()

"""
Define Simulation Loop
"""


def update():
    global timer, config_win, frame_counter, duration, paused, display_decimation, max_display_points_window, \
        phaseplot, phasexa, phaseya, phaseza, graph, data, path_length, ApEn, \
        measures_data, phase_line, voltage_line
    # Update the configuration window no matter what (look for pause requests and display decimation)
    paused, display_decimation = config_win.update(frame_counter)

    # If the system is not paused, run the simulation code
    if not paused:
        # Stop the simulation when the duration has completed (and perform appropriate shutdown)
        if sim.t >= duration:
            if save_raw_file:
                phase_file.close()
                voltage_file.close()
            timer.stop()

        # Warn the user when the transition to monitoring happens (if monitoring lag is used)
        if sim.t - sim.tick < begin_integration_time <= sim.t or \
                (begin_integration_time == 0 and sim.t == 0):
            print "Beginning Integration."

        # Update the simulation
        sim.update()

        # Prepare the data for any of the output conditions (condensed to one loop for efficiency)
        if inline_apen or inline_path_length or save_raw_file:
            phase_line = ""
            voltage_line = ""
            measures_data = []
            for _i in range(sim.number_of_PLLs):
                phase = sim.PLLs[_i].v(sim.PLLs[_i].next_phase_shift).real
                voltage = sim.PLLs[_i].previous_voltage.real
                measures_data.append(phase)
                measures_data.append(voltage)
                if save_raw_file:
                    phase_line = phase_line + str(phase) + ","
                    voltage_line = voltage_line + str(voltage) + ","

        # If monitoring has begin, conditionally perform outputs
        if sim.t >= begin_integration_time:
            if save_raw_file:
                phase_file.write("{0}\n".format(phase_line[0:-1]))
                voltage_file.write("{0}\n".format(voltage_line[0:-1]))
            if inline_apen:
                print ApEn.update(measures_data)
            if inline_path_length:
                print path_length.update(measures_data)

        # Visualize the system according to the display decimation
        if frame_counter % display_decimation == 0:
            if show_phase_plot:
                for _i in range(phaseplot.numLines):
                    if len(phasexa[_i]) == max_display_points_window:
                        phasexa[_i].popleft()
                    if len(phaseya[_i]) == max_display_points_window:
                        phaseya[_i].popleft()
                    if len(phaseza[_i]) == max_display_points_window:
                        phaseza[_i].popleft()
                    phasexa[_i].append(sim.PLLs[_i].v(sim.PLLs[_i].next_phase_shift).real)
                    phaseya[_i].append(sim.PLLs[_i].previous_voltage.real)
                    phaseza[_i].append(0)
                phaseplot.update(phasexa, phaseya, phaseza)
            if show_graphs:
                for _i in range(0, len(data)):
                    if len(data[_i]) == max_display_points_window:
                        data[_i].popleft()
                data[0].append(sim.last_input[0])
                data[1].append(sim.PLLs[0].detected_phase_log[-1])
                data[2].append(sim.PLLs[0].filtered_phase)
                data[3].append(sim.PLLs[0].next_phase_shift)
                data[4].append(sim.PLLs[0].v(sim.PLLs[0].next_phase_shift).real)
                data[5].append(sim.PLLs[0].previous_voltage)
                graph.update(data, frame_counter - max_display_points_window, frame_counter)

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