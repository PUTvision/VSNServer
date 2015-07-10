from common.VSNUtility import GainSampletimeTuple, ImageType, Config
from common.VSNPacket import ConfigurationPacketToClient


class VSNCamera:
    def __init__(self, client):
        self.__client = client
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

    def change_image_type(self, image_type: ImageType):
        self.__client.send(ConfigurationPacketToClient(image_type=image_type))
