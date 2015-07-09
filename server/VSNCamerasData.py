__author__ = 'Amin'

from common.VSNUtility import GainSampletimeTuple, ImageType, Config

import pickle


class VSNCameraData:
    def __init__(self):
        # data from camera
        self.activation_level = 0.0
        self.__activation_level_history = []
        self.percentage_of_active_pixels = 0.0
        self.__percentage_of_active_pixels_history = []
        # data to camera that is calculated periodically
        self.activation_neighbours = 0.0  # weighted activity of neighbouring nodes
        # internal counters of camera state
        self.ticks_in_low_power_mode = 0
        self.ticks_in_normal_operation_mode = 0
        # camera parameters
        self.flag_send_image = False
        self.image_type = ImageType.foreground
        self.__params_below_threshold = GainSampletimeTuple(Config.clients['parameters_below_threshold']['gain'],
                                                            Config.clients['parameters_below_threshold']['sample_time'])
        self.__params_above_threshold = GainSampletimeTuple(Config.clients['parameters_above_threshold']['gain'],
                                                            Config.clients['parameters_above_threshold']['sample_time'])
        self.__activation_level_threshold = Config.clients['activation_level_threshold']
        self.__parameters = self.__params_below_threshold  # sample time and gain at startup
        # flag indicating that parameters should be send to camera
        self.flag_parameters_changed = True

    @property
    def activation_level_history(self):
        return self.__activation_level_history

    @property
    def percentage_of_active_pixels_history(self):
        return self.__percentage_of_active_pixels_history

    @property
    def parameters(self):
        return self.__parameters

    def clear_history(self):
        self.__activation_level_history = []
        self.__percentage_of_active_pixels_history = []
        self.ticks_in_normal_operation_mode = 0
        self.ticks_in_low_power_mode = 0

    def update(self, activation_level, percentage_of_active_pixels):
        self.activation_level = activation_level
        self.percentage_of_active_pixels = percentage_of_active_pixels

        self.__update_history()

        self.__update_ticks_counters()

    def __update_ticks_counters(self):
        if self.activation_level < self.__activation_level_threshold:
            self.ticks_in_low_power_mode += 10
        else:
            self.ticks_in_normal_operation_mode += 1

    def __update_history(self):
        if self.activation_level < self.__activation_level_threshold:
            number_of_elements_to_append = 10
        else:
            number_of_elements_to_append = 1

        for i in range(0, number_of_elements_to_append):
            self.__activation_level_history.append(self.activation_level)
            self.__percentage_of_active_pixels_history.append(self.percentage_of_active_pixels)


class VSNCameras:
    def __init__(self):
        # TODO: this should be automatically created or even put inside the CameraData class
        self.__dependency_table = {
            'picam01': [0.0, 0.5, 0.2, 0.0, 0.0],
            'picam02': [0.5, 0.0, 0.5, 0.1, 0.0],
            'picam03': [0.1, 0.5, 0.0, 0.5, 0.2],
            'picam04': [0.0, 0.1, 0.5, 0.0, 0.5],
            'picam05': [0.0, 0.0, 0.2, 0.5, 0.0]
        }

        self.cameras = {}
        # TODO: remove the automatic creation of 4 cameras and do it as new cameras connect
        self.add_camera(1)
        self.add_camera(2)
        self.add_camera(3)
        self.add_camera(4)
        self.add_camera(5)

    def choose_camera_to_stream(self, camera_name):
        for key in self.cameras:
            self.cameras[key].flag_send_image = False
        self.cameras[str(camera_name)].flag_send_image = True

    def get_flag_send_image(self, camera_number):
        camera_name = self.__convert_camera_number_to_camera_name(camera_number)
        return self.cameras[camera_name].flag_send_image

    def get_activation_neighbours(self, camera_number):
        camera_name = self.__convert_camera_number_to_camera_name(camera_number)
        return self.cameras[camera_name].activation_neighbours

    def get_percentage_of_active_pixels(self, camera_number):
        camera_name = self.__convert_camera_number_to_camera_name(camera_number)
        return self.cameras[camera_name].percentage_of_active_pixels

    def get_status(self, camera_number):
        camera_name = self.__convert_camera_number_to_camera_name(camera_number)
        return (camera_name,
                self.cameras[camera_name].percentage_of_active_pixels,
                self.cameras[camera_name].activation_level,
                self.cameras[camera_name].activation_neighbours,
                self.cameras[camera_name].parameters.gain,
                self.cameras[camera_name].parameters.sample_time,
                self.cameras[camera_name].ticks_in_low_power_mode,
                self.cameras[camera_name].ticks_in_normal_operation_mode
                )

    def add_camera(self, camera_number):
        camera_name = self.__convert_camera_number_to_camera_name(camera_number)
        self.cameras[camera_name] = VSNCameraData()

    def __convert_camera_number_to_camera_name(self, camera_number):
        camera_name = "picam" + str(camera_number).zfill(2)
        return camera_name

    def save_cameras_data_to_files(self):
        for i in range(1, 6):
            camera_name = self.__convert_camera_number_to_camera_name(i)
            with open(camera_name + ".txt", "wb") as file:
                pickle.dump(self.cameras[camera_name], file)

    def load_cameras_data_from_files(self):
        for i in range(1, 6):
            camera_name = self.__convert_camera_number_to_camera_name(i)
            with(camera_name + ".txt", "rb") as file:
                self.cameras[camera_name] = pickle.load(file)

    def clear_cameras_data(self):
        for i in range(1, 6):
            camera_name = self.__convert_camera_number_to_camera_name(i)
            self.cameras[camera_name].clear_history()

    def update_state(self, camera_number, activation_level, percentage_of_active_pixels):
        camera_name = self.__convert_camera_number_to_camera_name(camera_number)

        self.cameras[camera_name].update(activation_level, percentage_of_active_pixels)

        return self.__calculate_neighbour_activation_level(camera_name)

    def __calculate_neighbour_activation_level(self, camera_name):
        # TODO: change it to check against the real number of cameras in the system
        self.cameras[camera_name].activation_neighbours = 0.0
        for idx in range(0, len(self.cameras) - 1):
            # idx+1 is used because cameras are numbered 1, 2, 3, 4, 5
            current_camera_name = "picam" + str(idx + 1).zfill(2)
            self.cameras[camera_name].activation_neighbours += \
                self.__dependency_table[camera_name][idx] * self.cameras[current_camera_name].percentage_of_active_pixels

        return self.cameras[camera_name].activation_neighbours

        # self._activation_neighbours[node_index] = 0
        # for idx in range(0, 3):
        #    self._activation_neighbours[node_index] += \
        #        dependency_table[node_name][idx] * self._graphsController._percentages[idx]
