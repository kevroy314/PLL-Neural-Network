__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

import pyqtgraph as pg  # For GUI


class GraphVisualizer:
    def __init__(self, num_rows, colors, titles):
        self.num_rows = num_rows
        self.colors = colors
        self.titles = titles

        self.win = pg.GraphicsWindow(title="PLL Example Animated")
        self.win.resize(1000, 600)
        self.win.setWindowTitle('PLL State Graphs')

        # Set up plot environment
        self.plotAreas = []
        self.curves = []
        for i in range(0, self.num_rows):
            self.plotAreas.append(self.win.addPlot())
            self.win.nextRow()
            self.plotAreas[i].enableAutoRange('xy', True)
            self.legend = pg.LegendItem(offset=(0, 1))
            for j in range(0, len(colors)):
                self.curves.append(self.plotAreas[i].plot(pen=self.colors[j]))
                self.legend.addItem(self.curves[j], self.titles[j])
            self.legend.setParentItem(self.plotAreas[i])

    def update(self, _d):
        for i in range(0, len(self.curves)):
                self.curves[i].setData(_d[i])