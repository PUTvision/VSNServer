__author__ = 'Amin'

from server.VSNCamerasData import VSNCameras

from pyqtgraph.Qt import QtGui
import pyqtgraph as pg


class VSNHistoryPlotter:
    def __init__(self):
        self.cameras = VSNCameras()
        self._win_activation = None
        self._win_percentage = None
        self._win_activation_binary = None

        self._load_data()
        self._create_graph_window()
        self._add_graphs_activation()
        self._add_graphs_percentage()
        self._add_graphs_activation_binary()
        self._print_power_mode()

    def _create_graph_window(self):
        # set default background color to white
        pg.setConfigOption('background', 'w')
        # open the plot window, set properties
        self._win_activation = pg.GraphicsWindow(title="VSN history plotter activity")
        self._win_activation.resize(1750, 1000)

        self._win_percentage = pg.GraphicsWindow(title="VSN history plotter percentage")
        self._win_percentage.resize(1750, 1000)

        self._win_activation_binary = pg.GraphicsWindow(title="VSN history plotter activity")
        self._win_activation_binary.resize(1750, 1000)

    def _load_data(self):
        self.cameras.load_cameras_data_from_files()

    def _add_graphs_activation_binary(self):
        for i in range(0, len(self.cameras.cameras)):
            name = "picam" + str(i+1).zfill(2)
            plot_title = "PiCam" + str(i+1).zfill(2)
            data = self.cameras.cameras[name].activation_level_history
            activation_level_binary_history = []
            for value in data:
                if value >= 15:
                    activation_level_binary_history.append(1)
                else:
                    activation_level_binary_history.append(0)

            #if i % 2 == 0:
            self._win_activation_binary.nextRow()
            cam_plot = self._win_activation_binary.addPlot(title=plot_title)
            curve = cam_plot.plot(pen=pg.mkPen('r', width=2))
            cam_plot.setrange(0, len(data))
            cam_plot.setYRange(0, 2)
            curve.setData(activation_level_binary_history)

    def _add_graphs_activation(self):
        for i in range(0, len(self.cameras.cameras)):
            name = "picam" + str(i+1).zfill(2)
            plot_title = "PiCam" + str(i+1).zfill(2)
            #if i % 2 == 0:
            self._win_activation.nextRow()
            cam_plot = self._win_activation.addPlot(title=plot_title)
            curve = cam_plot.plot(pen='r')
            cam_plot.setYRange(0, 100)
            data = self.cameras.cameras[name].activation_level_history
            curve.setData(data)

    def _add_graphs_percentage(self):
        for i in range(0, len(self.cameras.cameras)):
            name = "picam" + str(i+1).zfill(2)
            plot_title = "PiCam" + str(i+1).zfill(2)
            #if i % 2 == 0:
            self._win_percentage.nextRow()
            cam_plot = self._win_percentage.addPlot(title=plot_title)
            curve = cam_plot.plot(pen='r')
            cam_plot.setYRange(0, 100)
            data = self.cameras.cameras[name].percentage_of_active_pixels_history
            curve.setData(data)

    def _print_power_mode(self):
        for i in range(0, len(self.cameras.cameras)):
            name = "picam" + str(i+1).zfill(2)
            print(name +
                  ": " +
                  "low power ticks: " +
                  str(self.cameras.cameras[name].ticks_in_low_power_mode) +
                  ", " +
                  "normal operation ticks: " +
                  str(self.cameras.cameras[name].ticks_in_normal_operation_mode) +
                  "\r\n")


if __name__ == "__main__":
    history_plotter = VSNHistoryPlotter()

    QtGui.QApplication.instance().exec_()
