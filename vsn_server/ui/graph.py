import pyqtgraph as pg
import numpy as np
import asyncio


class VSNGraphController:
    __graphs = []
    __graphs_ids = set()

    # current activation level
    __activations = np.zeros((30, 1))

    # white pixel percentage
    __percentages = np.zeros((30, 1))

    __updating_task = None

    @classmethod
    def set_new_values(cls, camera_id, activation, percentage):
        cls.__activations[camera_id] = activation
        cls.__percentages[camera_id] = percentage

    @classmethod
    def create_plot(cls, camera_id: int, plot_item):
        if cls.__updating_task is None:
            cls.__updating_task = asyncio.get_event_loop().create_task(
                cls.__update_graphs())

        new_plot = VSNGraph(camera_id, plot_item)
        cls.__graphs.append(new_plot)
        return new_plot

    @classmethod
    async def __update_graphs(cls):
        while True:
            for graph in cls.__graphs:
                graph_id = graph.id
                graph.update_graph(cls.__activations[graph_id],
                                   cls.__percentages[graph_id])
            await asyncio.sleep(0.1)

    @classmethod
    def stop_updating(cls):
        cls.__updating_task.cancel()


class VSNGraph:
    def __init__(self, camera_id, plot_item):
        self.__id = camera_id
        self.__plot_title = 'Camera %i' % camera_id

        self.__white_pixels_percentage = np.zeros(1)
        # self.neighbouring_node_activation_level = 0.0
        self.__activation_level_history = np.zeros(200)

        # graph elements
        self.__curve = plot_item.plot(pen='r')
        self.__bar = pg.PlotCurveItem([0, 200], [0], stepMode=True, fillLevel=0,
                                      brush=(0, 0, 255, 20))
        plot_item.addItem(self.__bar)

        # set the scale of the plot
        plot_item.setYRange(0, 200)

    @property
    def id(self):
        return self.__id

    def update_graph(self, activation_level, white_pixels_percentage):
        self.__white_pixels_percentage = white_pixels_percentage
        self.__bar.setData([0, 20], self.__white_pixels_percentage)

        self.__activation_level_history = np.roll(
            self.__activation_level_history, -1)
        self.__activation_level_history[199] = activation_level
        self.__curve.setData(self.__activation_level_history)
