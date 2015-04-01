__author__ = 'Amin'

import struct


class VSNPacket:
    def __init__(self):
         # https://docs.python.org/2/library/struct.html
        # !i:
        # ! => network (= big-endian)
        # i => int
        self._struct_format = "! i f f"
        self._prefixLength = struct.calcsize(self._struct_format)
        self._s = struct.Struct(self._struct_format)

        self.camera_number = 0
        self.white_pixels = 0.0
        self.activation_level = 0.0

    def set(self, camera_number, white_pixels, activation_level):
        self.camera_number = camera_number
        self.white_pixels = white_pixels
        self.activation_level = activation_level

    def pack_to_send(self):
        return self._s.pack(self.camera_number, self.white_pixels, self.activation_level)

    def unpack_from_receive(self, string):
        self.camera_number, self.white_pixels, self.activation_level = self._s.unpack(string)
