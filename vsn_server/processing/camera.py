import pickle

from vsn_server.common.packet import ConfigurationPacketToClient
from vsn_server.common.utility import GainSampletimeTuple, ImageType, Config


class VSNCameraHistory:
    def __init__(self, camera_id):
        self.__camera_id = camera_id
        self.__percentage_of_active_pixels_history = []
        self.__activation_level_history = []

        self.ticks_in_low_power_mode = 0
        self.ticks_in_normal_operation_mode = 0

    @property
    def camera_id(self):
        return self.__camera_id

    @property
    def percentage_of_active_pixels_history(self):
        return self.__percentage_of_active_pixels_history

    @property
    def activation_level_history(self):
        return self.__activation_level_history

    def add_percentage_of_active_pixels_to_history(self, percentage_of_active_pixels: float):
        self.__percentage_of_active_pixels_history.append(percentage_of_active_pixels)

    def add_activation_level_to_history(self, activation_level: float):
        self.__activation_level_history.append(activation_level)

    def clear_history(self):
        self.__percentage_of_active_pixels_history.clear()


class VSNCamera:
    def __init__(self, client):
        self.__client = client

        # data from camera
        self.__activation_level = 0.0
        self.__activation_level_history = []
        self.__percentage_of_active_pixels = 0.0
        self.__camera_history = VSNCameraHistory(client.id)

        # internal counters of camera state
        self.__ticks_in_low_power_mode = 0
        self.__ticks_in_normal_operation_mode = 0

        # camera parameters
        self.__params_below_threshold = GainSampletimeTuple(
            Config['clients']['parameters_below_threshold']['gain'],
            Config['clients']['parameters_below_threshold']['sample_time'])
        self.__params_above_threshold = GainSampletimeTuple(
            Config['clients']['parameters_above_threshold']['gain'],
            Config['clients']['parameters_above_threshold']['sample_time'])
        self.__activation_level_threshold = Config['clients']['activation_level_threshold']
        self.__parameters = self.__params_below_threshold  # sample time and gain at startup
        self.__currently_transmitting_image = False
        self.__currently_set_image_type = ImageType.foreground

        self.__activation_neighbours = 0.0

    def __update_ticks_counters(self):
        if self.__activation_level < self.__activation_level_threshold:
            self.__ticks_in_low_power_mode += 10
        else:
            self.__ticks_in_normal_operation_mode += 1

    def __update_history(self):
        if self.__activation_level < self.__activation_level_threshold:
            number_of_elements_to_append = 10
        else:
            number_of_elements_to_append = 1

        for i in range(0, number_of_elements_to_append):
            self.__camera_history.add_activation_level_to_history(self.__activation_level)
            self.__camera_history.add_percentage_of_active_pixels_to_history(self.__percentage_of_active_pixels)

        self.__camera_history.ticks_in_low_power_mode = self.__ticks_in_low_power_mode
        self.__camera_history.ticks_in_normal_operation_mode = self.__ticks_in_normal_operation_mode

    @property
    def id(self):
        return self.__client.id

    @property
    def percentage_of_active_pixels(self):
        return self.__percentage_of_active_pixels

    @property
    def activation_level(self):
        return self.__activation_level

    @property
    def activation_level_history(self):
        return self.__activation_level_history

    @property
    def ticks_in_low_power_mode(self):
        return self.__ticks_in_low_power_mode

    @property
    def ticks_in_normal_operation_mode(self):
        return self.__ticks_in_normal_operation_mode

    @property
    def parameters(self):
        return self.__parameters

    def clear_history(self):
        self.__activation_level_history = []
        self.__camera_history.clear_history()
        self.__ticks_in_normal_operation_mode = 0
        self.__ticks_in_low_power_mode = 0

    def update(self, activation_level, percentage_of_active_pixels):
        self.__activation_level = activation_level
        self.__percentage_of_active_pixels = percentage_of_active_pixels

        self.__update_history()

        self.__update_ticks_counters()

    def change_image_type(self, image_type: ImageType):
        if self.__currently_set_image_type != image_type:
            self.__client.send(ConfigurationPacketToClient(image_type=image_type))
            self.__currently_set_image_type = image_type

    def start_sending_image(self):
        if not self.__currently_transmitting_image:
            self.__client.send(ConfigurationPacketToClient(send_image=True))
            self.__currently_transmitting_image = True

    def stop_sending_image(self):
        if self.__currently_transmitting_image:
            self.__client.send(ConfigurationPacketToClient(send_image=False))
            self.__currently_transmitting_image = False

    def save_camera_history_to_file(self, file):
        pickle.dump(self.__camera_history, file)

    def update_software(self, pkgs_to_update: list):
        self.__client.send(ConfigurationPacketToClient(pkgs_to_update=pkgs_to_update))
