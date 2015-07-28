from server.VSNCamera import VSNCamera

from vsn.common.VSNUtility import Config


class VSNCameras:
    def __init__(self):
        self.__dependency_table = Config.dependencies
        self.__cameras = {}

    @property
    def cameras(self):
        return self.__cameras

    @staticmethod
    def __convert_camera_number_to_camera_name(camera_number):
        camera_name = "picam" + str(camera_number).zfill(2)
        return camera_name

    def __calculate_neighbour_activation_level(self, camera_name: str):
        self.__cameras[camera_name].activation_neighbours = 0.0
        for current_camera_name, camera in self.__cameras.items():
            self.__cameras[camera_name].activation_neighbours += \
                self.__dependency_table[camera_name][camera.id - 1] * \
                self.__cameras[current_camera_name].percentage_of_active_pixels

        return self.__cameras[camera_name].activation_neighbours

    def choose_camera_to_stream(self, camera_name: str):
        for key in self.__cameras:
            if key != camera_name:
                self.__cameras[key].stop_sending_image()
        self.__cameras[camera_name].start_sending_image()

    def get_activation_neighbours(self, camera_number):
        camera_name = self.__convert_camera_number_to_camera_name(camera_number)
        return self.__cameras[camera_name].activation_neighbours

    def get_percentage_of_active_pixels(self, camera_number):
        camera_name = self.__convert_camera_number_to_camera_name(camera_number)
        return self.__cameras[camera_name].percentage_of_active_pixels

    def get_status(self, camera_number):
        camera_name = self.__convert_camera_number_to_camera_name(camera_number)
        return (camera_name,
                self.__cameras[camera_name].percentage_of_active_pixels,
                self.__cameras[camera_name].activation_level,
                self.__cameras[camera_name].activation_neighbours,
                self.__cameras[camera_name].parameters.gain,
                self.__cameras[camera_name].parameters.sample_time,
                self.__cameras[camera_name].ticks_in_low_power_mode,
                self.__cameras[camera_name].ticks_in_normal_operation_mode
                )

    def set_image_type(self, camera_name: str, image_type):
        self.__cameras[camera_name].change_image_type(image_type)

    def add_camera(self, client):
        camera_name = self.__convert_camera_number_to_camera_name(client.id)
        self.__cameras[camera_name] = VSNCamera(client)

    def save_cameras_data_to_files(self):
        for camera_name, camera in self.__cameras.items():
            with open(camera_name + ".txt", "wb") as file:
                camera.save_camera_history_to_file(file)

    def clear_cameras_data(self):
        for camera_name in self.__cameras:
            self.__cameras[camera_name].clear_history()

    def update_state(self, camera_number, activation_level, percentage_of_active_pixels):
        camera_name = self.__convert_camera_number_to_camera_name(camera_number)
        self.__cameras[camera_name].update(activation_level, percentage_of_active_pixels)

        return self.__calculate_neighbour_activation_level(camera_name)

    def update_camera_software(self, camera_name: str, pkgs_to_update: list):
        self.__cameras[camera_name].update_software(pkgs_to_update)
