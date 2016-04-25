import pickle

from vsn_server.connectivity.packets import ConfigurationPacket
from vsn_server.common.utility import GainSampletimeTuple, ImageType, Config

from itertools import repeat


class CameraHistory:
    def __init__(self, camera_id):
        self._camera_id = camera_id
        self._active_pixels_prcnt_history = []
        self._activation_level_history = []

        self.ticks_in_low_power_mode = 0
        self.ticks_in_normal_mode = 0

    @property
    def camera_id(self):
        return self._camera_id

    @property
    def percentage_of_active_pixels_history(self):
        return self._active_pixels_prcnt_history

    @property
    def activation_level_history(self):
        return self._activation_level_history

    def add_activation_level(self, activation_level: float, times: int=1):
            self._activation_level_history.extend(
                repeat(activation_level, times))

    def add_active_pixels_prcnt(self, active_pixels_prcnt: float, times: int=1):
        self._active_pixels_prcnt_history.append(repeat(active_pixels_prcnt,
                                                        times))

    def clear(self):
        self._active_pixels_prcnt_history.clear()
        self._activation_level_history.clear()
        self.ticks_in_low_power_mode = 0
        self.ticks_in_normal_mode = 0


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

    def change_image_type(self, image_type: ImageType):
        if self.__currently_set_image_type != image_type:
            self.__client.send(ConfigurationPacket(image_type='df'))
            self.__currently_set_image_type = image_type

    def start_sending_image(self):
        if not self.__currently_transmitting_image:
            self.__client.send(ConfigurationPacket(send_image=True))
            self.__currently_transmitting_image = True

    def stop_sending_image(self):
        if self.__currently_transmitting_image:
            self.__client.send(ConfigurationPacket(send_image=False))
            self.__currently_transmitting_image = False

    def save_camera_history_to_file(self, file):
        pickle.dump(self.__camera_history, file)
