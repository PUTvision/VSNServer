from PyQt5.QtGui import QPixmap, QImage

from vsn_server.common.utility import Config
from vsn_server.processing.camera import VSNCamera


class VSNCameras:
    __dependency_table = Config['dependencies']
    cameras = {}
    __preview_widgets = []

    @classmethod
    def add_preview_widget(cls, preview_widget):
        cls.__preview_widgets.append(preview_widget)

    @classmethod
    def process_image(cls, client, client_activity_level, cv_image):
        qt_image = QImage(cv_image, 320, 240, QImage.Format_Indexed8)
        cls.__preview_widgets[0].setPixmap(QPixmap.fromImage(qt_image))

    @classmethod
    def choose_camera_to_stream(cls, camera_id: int):
        for key in cls.cameras:
            if key != camera_id:
                cls.cameras[key].stop_sending_image()
        cls.cameras[camera_id].start_sending_image()

    @classmethod
    def get_activation_neighbours(cls, camera_id: int):
        return cls.cameras[camera_id].activation_neighbours

    @classmethod
    def get_percentage_of_active_pixels(cls, camera_id: int):
        return cls.cameras[camera_id].percentage_of_active_pixels

    @classmethod
    def set_image_type(cls, camera_name: str, image_type):
        cls.cameras[camera_name].change_image_type(image_type)

    @classmethod
    def save_cameras_data_to_files(cls):
        for camera_name, camera in cls.cameras.items():
            with open(camera_name + ".txt", "wb") as file:
                camera.save_camera_history_to_file(file)
