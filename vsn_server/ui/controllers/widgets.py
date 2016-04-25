from PyQt5.QtWidgets import QWidget
from vsn_server.ui.views.camera_widget import Ui_CameraWidget
from PyQt5.QtGui import QPixmap, QImage
from vsn_server.processing.camera import CameraHistory
from vsn_server.common.utility import Config


class CameraWidget(QWidget):
    def __init__(self, parent: QWidget, name: str):
        super().__init__(parent)

        self.ui = Ui_CameraWidget()
        self.ui.setupUi(self)

        self._activation_threshold = Config['clients']['activation_threshold']
        self.activation_level = 0.0
        self.active_pixels_prcnt = 0.0

        self._history = CameraHistory(name)

    def set_frame(self, cv_image):
        image = QImage(cv_image, 320, 240, QImage.Format_Indexed8)
        self.ui.preview.setPixmap(QPixmap.fromImage(image))

    def update_state(self, activation_level, active_pixels_prcnt):
        self.activation_level = activation_level
        self.active_pixels_prcnt = active_pixels_prcnt

        if activation_level < self._activation_threshold:
            self._history.ticks_in_low_power_mode += 10
            self._history.add_activation_level(activation_level, 10)
            self._history.add_active_pixels_prcnt(active_pixels_prcnt, 10)
        else:
            self._history.ticks_in_normal_mode += 1
            self._history.add_activation_level(activation_level)
            self._history.add_active_pixels_prcnt(active_pixels_prcnt)
