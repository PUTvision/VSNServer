__author__ = 'Amin'

from client.VSNPicam import VSNPicam

if __name__ == '__main__':
    picam = VSNPicam('picam01', 0)
    picam.start('150.254.47.164')
