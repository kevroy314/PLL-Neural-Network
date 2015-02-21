__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

from pyqtgraph.Qt import QtGui
import pyqtgraph as pg
from pylab import *


class TwoDVisualizer:
    def __init__(self, width, height, window_title="Phase Image"):
        """
        Create a 2D visualization for image data.

        :param width: The width of the image to be rendered.
        :param height: The height of the image to be rendered.
        """
        self.width = width
        self.height = height

        self.win = pg.GraphicsWindow(title=window_title)
        self.win.resize(300, 300)
        self.win.setWindowTitle(window_title)

        self.img = pg.ImageItem(autoLevels=False, levels=(-0.1, 0.1))  # Ignored unresolved reference ImageItem
        self.gradientWidget = pg.GradientWidget()  # Ignored unresolved reference GradientWidget
        self.gradientWidget.setTickColor(0, QtGui.QColor(255, 69, 00))
        self.gradientWidget.setTickColor(1, QtGui.QColor(0, 0, 128))
        self.lut = self.gradientWidget.getLookupTable(65536)
        self.img.setLookupTable(self.lut, update=False)
        data = np.random.randn(width, height)
        self.img.setImage(data)
        self.view = self.win.addViewBox()
        self.view.addItem(self.img)

    def update(self, _d, auto_levels=True):
        """
        Update the image visualization with new data and rescale of specified.

        :param _d: The 2D array of image data to be displayed
        :param auto_levels: (optional) If true, the color levels will dynamically shift relative to the input range on
                            each call. (default=True)
        """
        self.img.setImage(_d, autoLevels=auto_levels)
