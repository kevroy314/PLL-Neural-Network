__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

import pyqtgraph as pg


class GraphVisualizer:
    def __init__(self, num_rows, colors, titles, legend_layout="first",
                 window_width=1000, window_height=600, window_title="PLL State Graphs"):
        """
        Initialize a graph visualizer.

        :param num_rows: Number of rows of graph to display (too many will cause performance)
        :param colors: Colors of the different curves in each graph
        :param titles: Titles of the curves in each graph
        :param legend_layout: (optional, default="first") Determines where/if legends are displayed
                             "first" - only display legend on first graph
                             "all" - display legend on all graphs
                             "none" - don't display legend
        """

        # Store configuration
        self.num_rows = num_rows
        self.colors = colors
        self.titles = titles

        # Create window
        self.win = pg.GraphicsWindow(title=window_title)
        self.win.resize(window_width, window_height)
        self.win.setWindowTitle(window_title)

        # Set up plot environment
        self.plotAreas = []
        self.curves = []

        for i in range(0, self.num_rows):
            self.plotAreas.append(self.win.addPlot())
            self.win.nextRow()
            self.plotAreas[i].enableAutoRange('y', True)
            if legend_layout == "all" or (legend_layout == "first" and i == 0):
                self.legend = pg.LegendItem(offset=(0, 1))  # Ignored unresolved reference LegendItem
            for j in range(0, len(self.colors)):
                self.curves.append(self.plotAreas[i].plot(pen=self.colors[j]))
                if legend_layout == "all" or (legend_layout == "first" and i == 0):
                    self.legend.addItem(self.curves[j], self.titles[j])
            if legend_layout == "all" or (legend_layout == "first" and i == 0):
                self.legend.setParentItem(self.plotAreas[i])

    def update(self, _d, xmin=100, xmax=200):
        """
        Update the graph values with a new set of data.

        :param _d: The data (1D array where each element is an array of data to be plotted on each graph+curve)
        """
        if xmin < 0:
            xmin = 0
        for i in range(0, len(self.plotAreas)):
            self.plotAreas[i].getAxis("bottom").setRange(xmin, xmax)
        for i in range(0, len(self.curves)):
            self.curves[i].setData(_d[i])