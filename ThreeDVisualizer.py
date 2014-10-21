__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import scipy.ndimage as ndi
import numpy as np


class ThreeDVisualizer:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        # # Create a GL View widget to display data
        self.w = gl.GLViewWidget()
        self.w.show()
        self.w.setWindowTitle('GLSurfacePlot')
        self.w.setCameraPosition(distance=50)

        ## Add a grid to the view
        self.g = gl.GLGridItem()
        self.g.scale(1, 1, 1)
        self.g.setDepthValue(10)  # draw grid after surfaces since they may be translucent
        self.w.addItem(self.g)

        ## Animated example
        ## compute surface vertex data
        self.x = np.linspace(-8, 8, self.width + 1).reshape(self.width + 1, 1)
        self.y = np.linspace(-8, 8, self.height + 1).reshape(1, self.height + 1)

        ## create a surface plot, tell it to use the 'heightColor' shader
        ## since this does not require normal vectors to render (thus we
        ## can set computeNormals=False to save time when the mesh updates)
        self.p = gl.GLSurfacePlotItem(x=self.x[:, 0], y=self.y[0, :],
                                      colors=np.zeros((self.width, self.height, 4), dtype=float),
                                      computeNormals=False)
        #self.p.shader()['colorMap'] = np.array([0.2, 2, 0.5, 0.2, 1, 1, 0.2, 0, 2])
        #self.p.translate(10, 10, 0)
        self.w.addItem(self.p)

    def update(self, _i, _r, _index):
        colors = np.float32(_r)
        height = _i[_index % _i.shape[0]]
        height = np.zeros(height.shape)
        self.p.setData(z=height, colors=colors)