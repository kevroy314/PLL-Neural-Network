__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

from pyqtgraph.Qt import QtGui, QtCore  # For GUI
import pyqtgraph as pg  # For GUI
from PIL import Image
from lib.visualization.TwoDVisualizer import TwoDVisualizer
from lib.visualization.LinePlotVisualizer import LinePlotVisualizer
from lib.app_modules.ConfigurationWindow import ConfigurationWindow
from lib.app_modules.HelperFunctions import *
from lib.PLLs.Complex_PLL_Network import Complex_PLL_Network

"""
Initialize the Simulation
"""

paused = True
duration = 10
sim = Complex_PLL_Network(number_of_PLLs=5, sample_rate=400.0,
                          carrier_frequency=1.0, lowpass_cutoff_frequency=0.001,
                          filter_order=3, filter_window_size=100)

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

twod = TwoDVisualizer(int(render_width), int(sim.number_of_PLLs / render_width), "Real Phase Image")
twodimag = TwoDVisualizer(int(render_width), int(sim.number_of_PLLs / render_width), "Imaginary Phase Image")
phaseplot = LinePlotVisualizer(sim.number_of_PLLs, windowTitle="Phase Plot", distance=4.7625370521)
phasexa = []
phaseya = []
phaseza = []
for i in range(phaseplot.numLines):
    phasexa.append([])
    phaseya.append([])
    phaseza.append([])

lnint = LineIntegral(sim.number_of_PLLs)

display_decimation = config_win.display_decimation
frame_counter = 0

# Create loop timer
timer = QtCore.QTimer()

"""
Define Simulation Loop
"""


def update():
    global timer, twod, config_win, frame_counter, duration, paused, display_decimation, \
        phaseplot, phasexa, phaseya, phaseza, lnint
    paused, connectivity_matrix, display_decimation = config_win.update(sim.connectivity_matrix, frame_counter)
    if not paused:
        # Stop the simulation when the duration has completed
        if sim.t >= duration:
            timer.stop()

        sim.update();

        # Graph the PLL states according to the display decimation
        if frame_counter % display_decimation == 0:
            integral_data = []
            for _i in range(phaseplot.numLines):
                tpl = (sim.PLLs[_i].v(sim.PLLs[_i].next_phase_shift).real, sim.PLLs[_i].previous_voltage.real, 0)
                phasexa[_i].append(tpl[0])
                phaseya[_i].append(tpl[1])
                phaseza[_i].append(tpl[2])
                integral_data.append(tpl)
            lnint.update(integral_data)
            if sim.t - sim.tick < 2 <= sim.t:
                print lnint.getTotal()
            phaseplot.update(phasexa, phaseya, phaseza)

            image_data = array(np.zeros((sim.number_of_PLLs / render_width, render_width)), dtype=complex)
            for _i in range(0, sim.number_of_PLLs):
                row = np.floor(_i / render_width)
                col = _i % render_width
                image_data[row][col] = sim.PLLs[_i].v(sim.PLLs[_i].next_phase_shift)
            img_rotated = np.rot90(image_data, 3)
            twod.update(img_rotated.real, autoLevels=True)
            twodimag.update(img_rotated.imag, autoLevels=True)
            if render_video:
                # r, g, and b are 512x512 float arrays with values >= 0 and < 1.
                rgbArray = np.zeros((sim.number_of_PLLs / render_width, render_width, 3), 'uint8')
                rgbArray[..., 0] = image_data.real * 255
                rgbArray[..., 1] = 0
                rgbArray[..., 2] = image_data.imag * 255
                img = Image.fromarray(rgbArray)
                img.save('.\\video\\img_' + str(frame_counter).zfill(5) + '.png')
                realexporter = pg.exporters.ImageExporter.ImageExporter(twod.img)
                imagexporter = pg.exporters.ImageExporter.ImageExporter(twodimag.img)

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
timer.timeout.connect(update)
timer.start(0)

# # Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()