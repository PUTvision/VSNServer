__author__ = 'Amin'

from VSNPicam import VSNPicam

if __name__ == '__main__':
    picam = VSNPicam("picam01", 0)
    picam.start("127.0.0.1")
