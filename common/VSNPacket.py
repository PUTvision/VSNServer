from common.VSNUtility import Config


class ConfigurationPacketToClient:
    def __init__(self):
        self.dependencies = Config.dependencies
        self.parameters_below_threshold = Config.parameters_below_threshold
        self.parameters_above_threshold = Config.parameters_above_threshold


class DataPacketToServer:
    def __init__(self, camera_number, white_pixels, activation_level, flag_image_next, image=None):
        self.camera_number = camera_number
        self.white_pixels = white_pixels
        self.activation_level = activation_level
        self.flag_image_next = flag_image_next
        self.image = image

    def set(self, camera_number, white_pixels, activation_level, flag_image_next, image=None):
        self.camera_number = camera_number
        self.white_pixels = white_pixels
        self.activation_level = activation_level
        self.flag_image_next = flag_image_next
        self.image = image


class DataPacketToClient:
    def __init__(self, activation_neighbours, image_type, flag_send_image):
        self.activation_neighbours = activation_neighbours
        self.image_type = image_type
        self.flag_send_image = flag_send_image

    def set(self, activation_neighbours, image_type, flag_send_image):
        self.activation_neighbours = activation_neighbours
        self.image_type = image_type
        self.flag_send_image = flag_send_image
