__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

"""
Demonstrate use of GLLinePlotItem to draw cross-sections of a surface.

"""

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np

app = QtGui.QApplication([])
w = gl.GLViewWidget()
w.opts['distance'] = 40
w.show()
w.setWindowTitle('pyqtgraph example: GLLinePlotItem')

gx = gl.GLGridItem()
gx.rotate(90, 0, 1, 0)
gx.translate(-10, 0, 0)
w.addItem(gx)
gy = gl.GLGridItem()
gy.rotate(90, 1, 0, 0)
gy.translate(0, -10, 0)
w.addItem(gy)
gz = gl.GLGridItem()
gz.translate(0, 0, -10)
w.addItem(gz)


def fn(_x, _y):
    return np.cos((_x**2 + _y**2)**0.5)

n = 1
x = []
y = []
z = []

i = 2
end_i = 100
pts = np.vstack([x, y, z]).transpose()
plt = gl.GLLinePlotItem(pos=pts, color=pg.glColor((192, 255, 238)), width=(i+1)/10., antialias=True)
w.addItem(plt)

timer = QtCore.QTimer()


def update():
    global i, pts, plt, x, y, z, timer
    x.append(np.sin(i))
    y.append(np.cos(i))
    z.append(np.sin(i)*i/end_i)
    pts = np.vstack([x, y, z]).transpose()
    plt.setData(pos=pts)
    i += 0.1
    if i >= end_i:
        timer.stop()

timer.timeout.connect(update)
timer.start(0)

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
