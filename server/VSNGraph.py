__author__ = 'Amin'

import pyqtgraph as pg
import numpy as np


class VSNGraphController:
    def __init__(self):
        self._graphs = []
        self._win = None
        # TODO: remove this temporary buffers, put them into VSNGraph class and add appropriate methods
        # current activation level
        self._activations = np.zeros((5, 1))
        # white pixel percentage
        self._percentages = np.zeros((5, 1))

    def create_graph_window(self):
        # set default background color to white
        pg.setConfigOption('background', 'w')
        # open the plot window, set properties
        self._win = pg.GraphicsWindow(title='VSN activity monitor')
        self._win.resize(1400, 800)

        for i, graph in enumerate(self._graphs):
            if i > 0 and i % 2 == 0:
                self._win.nextRow()
            graph.add_graph(self._win)

    def add_new_graph(self):
        graph_number = len(self._graphs)
        new_graph = VSNGraph(graph_number)
        if len(self._graphs) % 2 == 0:
            self._win.nextRow()
        new_graph.add_graph(self._win)
        self._graphs.append(new_graph)

    def set_new_values(self, index, activation, percentage):
        self._activations[index] = activation
        self._percentages[index] = percentage

    def update_graphs(self):
        # TODO: remove this limitation to four objects
        for i, graph in enumerate(self._graphs):
            if i < len(self._graphs):
                graph.update_graph(self._activations[i], self._percentages[i])


class VSNGraph:
    def __init__(self, camera_number):
        self.plot_title = 'picam' + str(camera_number)

        self.white_pixels_percentage = np.zeros(1)
        # self.neighbouring_node_activation_level = 0.0
        self.activation_level_history = np.zeros(200)

        # graph elements
        self._curve = None
        self._bar = None

    def add_graph(self, window):
        # setup plot
        cam_plot = window.addPlot(title=self.plot_title)
        self._curve = cam_plot.plot(pen='r')
        self._bar = pg.PlotCurveItem([0, 200], [0], stepMode=True, fillLevel=0, brush=(0, 0, 255, 20))
        cam_plot.addItem(self._bar)
        # set the scale of the plot
        cam_plot.setYRange(0, 200)

    def update_graph(self, activation_level, white_pixels_percentage):
        self.white_pixels_percentage = white_pixels_percentage
        self._bar.setData([0, 20], self.white_pixels_percentage)

        self.activation_level_history = np.roll(self.activation_level_history, -1)
        self.activation_level_history[199] = activation_level
        self._curve.setData(self.activation_level_history)
