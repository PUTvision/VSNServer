#!/usr/bin/env python

from client.VSNReactor import VSNReactor
from client.VSNCamera import VSNPiCamera

if __name__ == '__main__':
    picam = VSNReactor(VSNPiCamera())
    picam.start()
