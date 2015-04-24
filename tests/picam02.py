from client import VSNPicam

__author__ = 'Amin'

if __name__ == '__main__':
    picam = VSNPicam("picam02", 1)
    picam.start("127.0.0.1")
