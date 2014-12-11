__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

from pyqtgraph.Qt import QtGui, QtCore  # For GUI
import pyqtgraph as pg  # For GUI
from lib.visualization.LinePlotVisualizer import LinePlotVisualizer
from lib.app_modules.ConfigurationWindow import ConfigurationWindow
from lib.app_modules.HelperFunctions import *
from lib.PLLs.Complex_PLL_Network import Complex_PLL_Network
import os
import time

show_ui = False

# Populate list of csv files in directory
input_dir = r'C:\Users\Kevin\Desktop\randomly chosen data\random_pre_dog\dog4_interictal'+'\\'
top_dir = os.path.split(os.path.relpath(input_dir))[-1]
timestring = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")

input_files = []

for _file in os.listdir(input_dir):
    if _file.endswith(".csv"):
        input_files.append(_file)

# Create output file
results_file = open('.\\results\\' + top_dir + '_path_length_' + timestring + '.csv', 'w')
result_file_apen_phase = open('.\\results\\' + top_dir + '_apen_phase_' + timestring + '.csv', 'w')
result_file_apen_voltage = open('.\\results\\' + top_dir + '_apen_voltage_' + timestring + '.csv', 'w')

# Set up application window
if show_ui:
    app = QtGui.QApplication([])
    pg.setConfigOptions(antialias=True)

for i in range(len(input_files)):
    print datetime.datetime.now().isoformat() + \
          ": Starting Iteration " + str(i) + ", Filename=\"" + input_files[i] + "\""
    """
    Initialize the Simulation
    """

    paused = False
    done = False
    begin_integration_time = 2
    duration = 4
    # Default Calibration: number_of_PLLs=16, sample_rate=400.0,
    # carrier_frequency=1.0, lowpass_cutoff_frequency=0.001,
    # filter_order=3, filter_window_size=100,
    sim = Complex_PLL_Network(number_of_PLLs=16, sample_rate=400.0,
                              carrier_frequency=1.0, lowpass_cutoff_frequency=0.001,
                              filter_order=3, filter_window_size=100,
                              in_signal_filename=input_dir+input_files[i])

    lnint = LineIntegral(sim.number_of_PLLs)
    ApEn = ApproximateEntropy(sim.number_of_PLLs, 2, 0.1)

    """
    Initialize the GUI
    """

    if show_ui:
        config_win = ConfigurationWindow(1, paused)

        phaseplot = LinePlotVisualizer(sim.number_of_PLLs, windowTitle="Phase Plot", distance=4.7625370521)
        phasexa = []
        phaseya = []
        phaseza = []
        for j in range(phaseplot.numLines):
            phasexa.append([])
            phaseya.append([])
            phaseza.append([])

        display_decimation = config_win.display_decimation
        frame_counter = 0

        # Create loop timer
        timer = QtCore.QTimer()

    """
    Define Simulation Loop
    """

    def update():
        global timer, config_win, frame_counter, duration, paused, display_decimation, \
            phaseplot, phasexa, phaseya, phaseza, lnint, ApEn, show_ui, done, sim, connectivity_matrix
        if show_ui:
            paused, connectivity_matrix, display_decimation = config_win.update(sim.connectivity_matrix, frame_counter)
        if sim.t >= duration:
                result = str(lnint.getTotal())[1:-1]
                resultApEnPhase = str(ApEn.getTotal(0))[1:-1]
                resultApEnVoltage = str(ApEn.getTotal(1))[1:-1]
                print "Integration Complete, Results=" + result
                print "-------------------------------------------------------"
                results_file.write(result + "\n")
                result_file_apen_phase.write(resultApEnPhase + "\n")
                result_file_apen_voltage.write(resultApEnVoltage + "\n")
                results_file.flush()
                result_file_apen_phase.flush()
                result_file_apen_voltage.flush()
                paused = True
                done = True
                if show_ui:
                    config_win.win.close()
                    phaseplot.win.close()
                    timer.stop()
        if not paused:
            # Stop the simulation when the duration has completed

            sim.update()

            integral_data = []
            for _i in range(sim.number_of_PLLs):
                tpl = (sim.PLLs[_i].v(sim.PLLs[_i].next_phase_shift).real, sim.PLLs[_i].previous_voltage.real, 0)
                integral_data.append(tpl)
            if sim.t - sim.tick < begin_integration_time <= sim.t:
                print "Beginning Integration."
            if sim.t >= begin_integration_time:
                lnint.update(integral_data)
                ApEn.update(integral_data)

            # Graph the PLL states according to the display decimation
            if show_ui:
                if frame_counter % display_decimation == 0:
                    for _i in range(phaseplot.numLines):
                        tpl = (sim.PLLs[_i].v(sim.PLLs[_i].next_phase_shift).real, sim.PLLs[_i].previous_voltage.real, 0)
                        phasexa[_i].append(tpl[0])
                        phaseya[_i].append(tpl[1])
                        phaseza[_i].append(tpl[2])
                    phaseplot.update(phasexa, phaseya, phaseza)

                # Iterate the display frame counter
                frame_counter += 1

    """
    Begin the Simulation and GUI
    """

    # Start event loop and wait until done
    if show_ui:
        # Begin Simulation
        timer.timeout.connect(update)
        timer.start(0)

        QtGui.QApplication.instance().exec_()

        while timer.isActive():
            time.sleep(0.05)
    else:
        while not done:
            update()