__author__ = 'Amin'

from VSNPicam import VSNPicam

if __name__ == '__main__':
    picam = VSNPicam("picam02", 1)

    picam.start()
