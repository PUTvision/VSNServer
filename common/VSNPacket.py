__author__ = 'Amin'

import struct

from enum import Enum

# Definitions of DTOs - Data Transfer Objects used for moving data
# from the network stream to higher level of processing

# TODO: convert this classes to simple struct like objects ...
# TODO: ... and offer methods that invoke appropriate action based on the data provided (Clean Code chapter 6)

class ImageType(Enum):
    foreground = 'fg'
    background = 'bg'
    difference = 'df'

# struct usage:
# https://docs.python.org/2/library/struct.html
# !i:
# ! => network (= big-endian)
# i => int

class VSNPacket:
    def __init__(self):
        self._struct_format = "! i f f ?"
        self._prefixLength = struct.calcsize(self._struct_format)
        self._s = struct.Struct(self._struct_format)

        self.camera_number = 0
        self.white_pixels = 0.0
        self.activation_level = 0.0
        self.flag_image_next = False

    def set(self, camera_number, white_pixels, activation_level, flag_image_next):
        self.camera_number = camera_number
        self.white_pixels = white_pixels
        self.activation_level = activation_level
        self.flag_image_next = flag_image_next

    def pack_to_send(self):
        return self._s.pack(
            self.camera_number,
            self.white_pixels,
            self.activation_level,
            self.flag_image_next
        )

    def unpack_from_receive(self, string):
        self.camera_number, self.white_pixels, self.activation_level, self.flag_image_next = self._s.unpack(string)


class VSNPacketImage:
    def __init__(self):
        self._image = None

    def set(self, image_as_string):
        self._image = image_as_string


class VSNPacketToClient:
    def __init__(self):
        self._struct_format = "! f 2s ?"
        self._prefixLength = struct.calcsize(self._struct_format)
        self._s = struct.Struct(self._struct_format)

        self.activation_neighbours = 0.0
        self.image_type = ImageType.foreground
        self.flag_send_image = False

    def set(self, activation_neighbours, image_type, flag_send_image):
        self.activation_neighbours = activation_neighbours
        self.image_type = image_type
        self.flag_send_image = flag_send_image

    def pack_to_send(self):
        return self._s.pack(self.activation_neighbours, bytes(self.image_type.value, encoding='utf-8'),
                            self.flag_send_image)

    def unpack_from_receive(self, string):
        self.activation_neighbours, self.image_type, self.flag_send_image = self._s.unpack(string)
        print(self.image_type)


class VSNPacketToClientParameters:
    def __init__(self):
        self._struct_format = "! 2s ? f f f f f"
        self._prefixLength = struct.calcsize(self._struct_format)
        self._s = struct.Struct(self._struct_format)

        self.image_type = ImageType.foreground
        self.flag_send_image = False
        self.threshold = 10.0
        self.gain_below_threshold = 2.0
        self.sample_time_below_threshold = 1.0
        self.gain_above_threshold = 0.1
        self.sample_time_above_threshold = 0.1

    def set(self, image_type,
            flag_send_image,
            threshold,
            gain_below,
            sample_time_below,
            gain_above,
            sample_time_above
            ):
        self.image_type = image_type
        self.flag_send_image = flag_send_image
        self.threshold = threshold
        self.gain_below_threshold = gain_below
        self.sample_time_below_threshold = sample_time_below
        self.gain_above_threshold = gain_above
        self.sample_time_above_threshold = sample_time_above

    def pack_to_send(self):
        return self._s.pack(
            self.image_type,
            self.flag_send_image,
            self.threshold,
            self.gain_below_threshold,
            self.sample_time_below_threshold,
            self.gain_above_threshold,
            self.sample_time_above_threshold
        )

    def unpack_from_receive(self, string):
        self.image_type, \
        self.flag_send_image, \
        self.threshold, \
        self.gain_below_threshold, \
        self.sample_time_below_threshold, \
        self.gain_above_threshold, \
        self.sample_time_above_threshold \
            = self._s.unpack(string)
