__author__ = 'Amin'


class GainSampletimeTuple:
    def __init__(self, gain, sample_time):
        self.gain = gain
        self.sample_time = sample_time

def enum(**enums):
    return type('Enum', (), enums)
