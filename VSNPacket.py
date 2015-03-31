__author__ = 'Amin'

import struct


class VSNPacket:
    def __init__(self):
         # https://docs.python.org/2/library/struct.html
        # !i:
        # ! = network (= big-endian)
        # i = int
        self._struct_format = "! i i i i"
        self._prefixLength = struct.calcsize(self._struct_format)
        self._s = struct.Struct(self._struct_format)

        self.channelsValues = [0, 0, 0, 0]

    def prepare_to_send(self, values):
        self.channelsValues[0] = values[0]
        self.channelsValues[1] = values[1]
        self.channelsValues[2] = values[2]
        self.channelsValues[3] = values[3]

        self._s.pack(self.channelsValues)
        #TODO - check it this method is working and prepare another one for unpacking the data

    def pack(self, *values):
        return self._s.pack(*values)

    def unpack(self, string):
        return self._s.unpack(string)
