#!/usr/bin/env python

from client.VSNReactor import VSNReactor
from client.VSNCamera import VSNCVCamera

if __name__ == '__main__':
    picam = VSNReactor(VSNCVCamera(camera_number=0))
    picam.start()
