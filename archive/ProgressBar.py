__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

import time
from PyQt4 import QtGui


class ProgressBar(QtGui.QWidget):
    def __init__(self, parent=None, total=20):
        super(ProgressBar, self).__init__(parent)
        self.setPalette(QtGui.QPalette(QtGui.QColor("black")))
        self.progressbar = QtGui.QProgressBar()
        self.progressbar.setMinimum(1)
        self.progressbar.setMaximum(total)
        main_layout = QtGui.QGridLayout()
        main_layout.addWidget(self.progressbar, 0, 1)
        self.setLayout(main_layout)
        self.setWindowTitle('Progress')

    def updateValue(self, newValue):
        self.progressbar.setValue(newValue)
        QtGui.qApp.processEvents()

    def test(self):
        while True:
            time.sleep(0.05)
            value = self.progressbar.value() + 1
            self.progressbar.setValue(value)
            QtGui.qApp.processEvents()
            if (value >= self.progressbar.maximum()):
                break