import pyqtgraph as pg
import numpy as np


class VSNGraphController:
    def __init__(self):
        self.__graphs = []
        self.__graphs_ids = set()

        # current activation level
        self.__activations = np.zeros((30, 1))
        # white pixel percentage
        self.__percentages = np.zeros((30, 1))

        # set default background color to white
        pg.setConfigOption('background', 'w')
        # open the plot window, set properties
        self.__win = pg.GraphicsWindow(title='VSN activity monitor')
        self.__win.resize(1400, 800)

    def update_graphs(self):
        for graph in self.__graphs:
            graph_id = graph.id
            graph.update_graph(self.__activations[graph_id], self.__percentages[graph_id])

    def add_graph(self, camera_id: int):
        if camera_id not in self.__graphs_ids:
            new_graph = VSNGraph(camera_id)
            new_graph.add_graph(self.__win)
            self.__graphs.append(new_graph)
            self.__graphs_ids.add(camera_id)

    def set_new_values(self, index, activation, percentage):
        self.__activations[index] = activation
        self.__percentages[index] = percentage

    def close(self):
        self.__win.close()


class VSNGraph:
    def __init__(self, camera_id):
        self.__id = camera_id
        self.__plot_title = 'picam' + str(camera_id).zfill(2)

        self.__white_pixels_percentage = np.zeros(1)
        # self.neighbouring_node_activation_level = 0.0
        self.__activation_level_history = np.zeros(200)

        # graph elements
        self.__curve = None
        self.__bar = None

    @property
    def id(self):
        return self.__id

    def add_graph(self, window):
        # setup plot
        cam_plot = window.addPlot(title=self.__plot_title, row=(self.__id - 1) // 2, col=(self.__id - 1) % 2)
        self.__curve = cam_plot.plot(pen='r')
        self.__bar = pg.PlotCurveItem([0, 200], [0], stepMode=True, fillLevel=0, brush=(0, 0, 255, 20))
        cam_plot.addItem(self.__bar)
        # set the scale of the plot
        cam_plot.setYRange(0, 200)

    def update_graph(self, activation_level, white_pixels_percentage):
        self.__white_pixels_percentage = white_pixels_percentage
        self.__bar.setData([0, 20], self.__white_pixels_percentage)

        self.__activation_level_history = np.roll(self.__activation_level_history, -1)
        self.__activation_level_history[199] = activation_level
        self.__curve.setData(self.__activation_level_history)
