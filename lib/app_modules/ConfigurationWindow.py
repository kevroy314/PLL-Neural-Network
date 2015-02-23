__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

from pyqtgraph.Qt import QtGui
import pyqtgraph as pg
import time


class ConfigurationWindow:
    def __init__(self, _display_decimation=10, pause=False):
        """
        Create a ConfigurationWindow for storing/modifying simulation properties.

        :param _display_decimation: The number of iterations displays should allow to complete before refreshing
                                    (default=10)
        """
        self.display_decimation = _display_decimation
        self.iteration = 0
        self.paused = pause

        self.last_update_call = time.time() * 1000
        self.timer_window_size = 10.0
        self.timer_last = 0.0

        self.win = QtGui.QMainWindow()
        self.win.resize(300, 200)
        self.win.show()
        self.win.setWindowTitle('Configuration')
        self.cw = QtGui.QWidget()
        self.win.setCentralWidget(self.cw)

        self.layout = QtGui.QGridLayout()
        self.cw.setLayout(self.layout)
        self.layout.setSpacing(0)

        display_text = "Pause"
        if pause:
            display_text = "Start"
        self.pauseBtn = QtGui.QPushButton(display_text, self.win)

        # noinspection PyUnresolvedReferences
        self.pauseBtn.clicked.connect(self.pause)
        self.layout.addWidget(self.pauseBtn, 0, 0)

        self.iterationLabel = QtGui.QLabel("")
        self.update_iteration_text()
        self.layout.addWidget(self.iterationLabel, 5, 0)
        self.decimationLabel = QtGui.QLabel("Display Decimation, min=0, no maximum.")
        # Ignored unresolved SpinBox reference
        self.decimationSpinBox = pg.SpinBox(value=self.display_decimation, bounds=[1, None], step=1)
        self.layout.addWidget(self.decimationLabel, 6, 0)
        self.layout.addWidget(self.decimationSpinBox, 7, 0)
        self.decimationSpinBox.sigValueChanged.connect(self.decimation_value_changed)

    def decimation_value_changed(self, _sb):
        """
        Get the value of the decimation control and store it in the decimation variable.

        :param _sb: The decimation control.
        """
        self.display_decimation = _sb.value()

    def update_iteration_text(self):
        current_time = time.time() * 1000
        time_diff = current_time - self.last_update_call
        averaged_time = (self.timer_last * ((self.timer_window_size - 1.0) / self.timer_window_size)) + (time_diff * (1 / self.timer_window_size))
        self.iterationLabel.setText("Iteration #: " + str(self.iteration) + " in " + str(averaged_time) + "ms")
        self.timer_last = averaged_time
        self.last_update_call = current_time

    def pause(self):
        """
            Toggle function for changing pause state.

        """
        self.paused = not self.paused
        display_text = "Pause"
        if self.paused:
            display_text = "Continue"
        self.pauseBtn.setText(display_text)

    def update(self, iteration=-1):
        """

        :return: The current config window parameters (pause, phase weight matrix, display decimation)
        """
        if iteration == -1:
            self.iterationLabel.setVisible(False)
        else:
            self.iteration = iteration
            self.update_iteration_text()

        return self.paused, self.display_decimation