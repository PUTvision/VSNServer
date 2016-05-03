from PyQt5.QtWidgets import QMainWindow
from vsn_server.ui.views.main_window import Ui_VSNServer
from vsn_server.ui.controllers.widgets import CameraWidget
from vsn_server.processing.reactor import Reactor
from vsn_server.connectivity.server import Server
from vsn_server.common.utility import Config


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_VSNServer()
        self.ui.setupUi(self)

        self._server = Server(
            Config['server']['listening_address'],
            Config['server']['listening_port'],
            Reactor(self)
        )

        self.cameras = {}

    def _get_neighbour_activation(self, camera_name: str):
        neighbour_activation = 0.0

        for neighbour_name, neighbour in self.cameras.items():
            neighbour_activation += (
                Config['dependencies'][camera_name][neighbour_name] *
                neighbour.active_pixels_prcnt)

        self.cameras[camera_name].activation_neighbours = neighbour_activation

        return neighbour_activation

    def add_camera(self, client):
        camera_widget = CameraWidget(self, client.id)
        for _ in range(5):
            self.ui.allCamerasLayout.addWidget(camera_widget)
        self.cameras[client.id] = camera_widget

    def update_camera_state(self, camera_id: int, activation_level: float,
                            active_pixels_prcnt: float):
        self.cameras[camera_id].update_state(activation_level,
                                             active_pixels_prcnt)

        return self._get_neighbour_activation(camera_id)
