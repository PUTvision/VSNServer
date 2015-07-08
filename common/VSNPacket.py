__author__ = 'Amin'

import pickle

from enum import Enum

# Definitions of DTOs - Data Transfer Objects used for moving data
# from the network stream to higher level of processing

# TODO: offer methods that invoke appropriate action based on the data provided (Clean Code chapter 6)

class ImageType(Enum):
    foreground = 'fg'
    background = 'bg'
    difference = 'df'


class VSNPacketToServer:
    def __init__(self, camera_number, white_pixels, activation_level, flag_image_next):
        self.camera_number = camera_number
        self.white_pixels = white_pixels
        self.activation_level = activation_level
        self.flag_image_next = flag_image_next

    def set(self, camera_number, white_pixels, activation_level, flag_image_next):
        self.camera_number = camera_number
        self.white_pixels = white_pixels
        self.activation_level = activation_level
        self.flag_image_next = flag_image_next

    @staticmethod
    def deserialize(data: bytes):
        obj = pickle.loads(data)

        if isinstance(obj, VSNPacketToServer):
            return obj
        else:
            raise TypeError('Deserialized object is not VSNPacketToServer object')

    def serialize(self):
        return pickle.dumps(self)


class VSNPacketToClient:
    def __init__(self, activation_neighbours, image_type, flag_send_image):
        self.activation_neighbours = activation_neighbours
        self.image_type = image_type
        self.flag_send_image = flag_send_image

    def set(self, activation_neighbours, image_type, flag_send_image):
        self.activation_neighbours = activation_neighbours
        self.image_type = image_type
        self.flag_send_image = flag_send_image

    @staticmethod
    def deserialize(data: bytes):
        obj = pickle.loads(data)

        if isinstance(obj, VSNPacketToClient):
            return obj
        else:
            raise TypeError('Deserialized object is not VSNPacketToClient object')

    def serialize(self):
        return pickle.dumps(self)
