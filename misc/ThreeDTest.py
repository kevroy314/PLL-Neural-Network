__author__ = 'Kevin'

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import scipy.ndimage as ndi
import numpy as np

## Create a GL View widget to display data
app = QtGui.QApplication([])
w = gl.GLViewWidget()
w.show()
w.setWindowTitle('pyqtgraph example: GLSurfacePlot')
w.setCameraPosition(distance=50)

width = 6
height = 10

## Add a grid to the view
g = gl.GLGridItem()
g.scale(1, 1, 1)
g.setDepthValue(10)  # draw grid after surfaces since they may be translucent
w.addItem(g)

## Animated example
## compute surface vertex data
x = np.linspace(-8, 8, width+1).reshape(width+1, 1)
y = np.linspace(-8, 8, height+1).reshape(1, height+1)
d = (x**2 + y**2) * 0.1
d2 = d ** 0.5 + 0.1

## precompute height values for all frames
phi = np.arange(0, np.pi*2, np.pi/20.)
z = np.sin(d[np.newaxis, ...] + phi.reshape(phi.shape[0], 1, 1)) / d2[np.newaxis, ...]


## create a surface plot, tell it to use the 'heightColor' shader
## since this does not require normal vectors to render (thus we
## can set computeNormals=False to save time when the mesh updates)
p = gl.GLSurfacePlotItem(x=x[:, 0], y=y[0, :])
p.shader()['colorMap'] = np.array([0.2, 2, 0.5, 0.2, 1, 1, 0.2, 0, 2])
w.addItem(p)

index = 0


def update():
    global p, z, index
    red = np.random.randn(width, height)
    timage_data = np.zeros((width, height, 4))
    timage_data[:, :, 3] = red
    index -= 1
    p.setData(z=z[index % z.shape[0]], colors=timage_data)

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(30)

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
