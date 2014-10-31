__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np


class LinePlotVisualizer:
    def __init__(self, numLines=1, windowTitle="Line Plot", distance=40):
        self.numLines = numLines
        self.windowTitle = windowTitle

        # Create Window
        self.win = gl.GLViewWidget()
        self.win.opts['distance'] = distance
        self.win.show()
        self.win.setWindowTitle(self.windowTitle)

        # Add Grid Lines
        self.gx = gl.GLGridItem()
        self.gx.rotate(90, 0, 1, 0)
        self.gx.translate(-10, 0, 0)
        self.win.addItem(self.gx)
        self.gy = gl.GLGridItem()
        self.gy.rotate(90, 1, 0, 0)
        self.gy.translate(0, -10, 0)
        self.win.addItem(self.gy)
        self.gz = gl.GLGridItem()
        self.gz.translate(0, 0, -10)
        self.win.addItem(self.gz)

        self.pts = []
        self.plts = []
        for i in range(self.numLines):
            self.pts.append(np.vstack([[], [], []]).transpose())
            self.plts.append(gl.GLLinePlotItem(color=pg.glColor((i, self.numLines*1.3)), antialias=True))
            self.win.addItem(self.plts[i])

    def update(self, x_array, y_array, z_array):

        """
        Update the values of the lines in the plot.

        :param x_array: A 2D array where each row is a 1D array representing the values for that line x.
        :param y_array: A 2D array where each row is a 1D array representing the values for that line y.
        :param z_array: A 2D array where each row is a 1D array representing the values for that line z.
        """

        minlen = min(len(x_array), len(y_array), len(z_array), self.numLines)

        for i in range(minlen):
            self.pts[i] = np.vstack([x_array[i], y_array[i], z_array[i]]).transpose()
            self.plts[i].setData(pos=self.pts[i])