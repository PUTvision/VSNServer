from enum import Enum
import yaml

from common.decorators import autoinitialized

@autoinitialized
class Config:
    @classmethod
    def initialize(cls):
        with open('config.yml', 'r') as stream:
            for key, value in yaml.load(stream).items():
                setattr(cls, key, value)


class GainSampletimeTuple:
    def __init__(self, gain, sample_time):
        self.gain = gain
        self.sample_time = sample_time


class ImageType(Enum):
    foreground = 'fg'
    background = 'bg'
    difference = 'df'
