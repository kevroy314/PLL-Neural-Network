__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

from pyqtgraph.Qt import QtGui, QtCore  # For GUI
import pyqtgraph as pg  # For GUI
from pylab import *  # For PLL


class TwoDVisualizer:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.win = pg.GraphicsWindow(title="PLL Example Animated")
        self.win.resize(300, 300)
        self.win.setWindowTitle('PLL Example Phase Image')

        self.img = pg.ImageItem(autoLevels=False, levels=(-0.1, 0.1))
        self.gradientWidget = pg.GradientWidget()
        self.gradientWidget.setTickColor(0, QtGui.QColor(255, 69, 00))
        self.gradientWidget.setTickColor(1, QtGui.QColor(0, 0, 128))
        self.lut = self.gradientWidget.getLookupTable(65536)
        self.img.setLookupTable(self.lut, update=False)
        data = np.random.randn(width, height)
        self.img.setImage(data)
        self.view = self.win.addViewBox()
        self.view.addItem(self.img)

    def update(self, _d, autoLevels=True):
        self.img.setImage(_d, autoLevels=autoLevels)
