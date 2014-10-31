__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

from pyqtgraph.Qt import QtGui, QtCore  # For GUI
import pyqtgraph as pg  # For GUI
#import pickle


class ConfigurationWindow:
    def __init__(self, _display_decimation=10):
        """
        Create a ConfigurationWindow for storing/modifying simulation properties.

        :param _display_decimation: The number of iterations displays should allow to complete before refreshing
                                    (default=10)
        """
        self.display_decimation = _display_decimation
        self.iteration = 0
        self.paused = False
        self.phase_weight_matrix = 0
        self.loaded_phase_weight_matrix = False

        self.win = QtGui.QMainWindow()
        self.win.resize(300, 200)
        self.win.show()
        self.win.setWindowTitle('Configuration')
        self.cw = QtGui.QWidget()
        self.win.setCentralWidget(self.cw)

        self.layout = QtGui.QGridLayout()
        self.cw.setLayout(self.layout)
        self.layout.setSpacing(0)

        self.pauseBtn = QtGui.QPushButton("Pause", self.win)

        self.pauseBtn.clicked.connect(self.pause)
        self.layout.addWidget(self.pauseBtn, 0, 0)

        '''
        self.saveWeightMatrixBtn = QtGui.QPushButton("Save Weight Matrix", self.win)

        self.saveWeightMatrixBtn.clicked.connect(self.save_weight_matrix)
        self.layout.addWidget(self.saveWeightMatrixBtn, 1, 0)

        self.loadWeightMatrixBtn = QtGui.QPushButton("Load Weight Matrix", self.win)

        self.loadWeightMatrixBtn.clicked.connect(self.load_weight_matrix)
        self.layout.addWidget(self.loadWeightMatrixBtn, 2, 0)
        '''
        self.iterationLabel = QtGui.QLabel("")
        self.updateIterationText()
        self.layout.addWidget(self.iterationLabel, 5, 0)
        self.decimationLabel = QtGui.QLabel("Display Decimation, min=0, no maximum.")
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

    '''
    def load_weight_matrix(self):
        filename = QtGui.QFileDialog.getOpenFileName(self.loadWeightMatrixBtn, "Load Weight Matrix", "", "*.phases")
        if filename != "":
            file_object = open(filename, 'r')
            self.phase_weight_matrix = pickle.load(file_object)
            self.loaded_phase_weight_matrix = True
            print_padded_matrix(self.phase_weight_matrix)

    def save_weight_matrix(self):
        filename = QtGui.QFileDialog.getSaveFileName(self.saveWeightMatrixBtn, "Save Weight Matrix", "", "*.phases")
        if filename != "":
            file_object = open(filename, 'w')
            pickle.dump(self.phase_weight_matrix, file_object)
            print_padded_matrix(self.phase_weight_matrix)
    '''
    def updateIterationText(self):
        self.iterationLabel.setText("Iteration #: " + str(self.iteration))

    def pause(self):
        """
            Toggle function for changing pause state.

        """
        self.paused = not self.paused
        display_text = "Pause"
        if self.paused:
            display_text = "Continue"
        self.pauseBtn.setText(display_text)

    def update(self, _phase_weight_matrix, iteration=-1):
        """

        :param _phase_weight_matrix: Phase Weight Matrix update for config window
        :return: The current config window parameters (pause, phase weight matrix, display decimation)
        """
        if iteration == -1:
            self.iterationLabel.setVisible(False)
        else:
            self.iteration = iteration
            self.updateIterationText()

        if not self.loaded_phase_weight_matrix:
            self.phase_weight_matrix = _phase_weight_matrix
        else:
            self.loaded_phase_weight_matrix = False
        return self.paused, self.phase_weight_matrix, self.display_decimation