__author__ = 'Amin'

from client.VSNPicam import VSNPicam

if __name__ == '__main__':
    picam = VSNPicam('picam02', 1)
    picam.start('127.0.0.1')
