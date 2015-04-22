__author__ = 'Amin'

from VSNPicam import VSNPicam

if __name__ == '__main__':
    picam = VSNPicam(video_capture_number=0)
    picam.start("192.168.0.10")