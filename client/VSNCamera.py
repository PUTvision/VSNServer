import cv2
import time

from abc import ABCMeta, abstractmethod
from threading import Thread

from common.VSNUtility import Config


class VSNCamera(metaclass=ABCMeta):
    @abstractmethod
    def grab_image(self):
        ...


class VSNCVCamera:
    def __init__(self, camera_number: int):
        self.__camera = cv2.VideoCapture(camera_number)
        self.__camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.__camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    def grab_image(self):
        return self.__camera.read()[1]


class VSNPiCamera:
    def __init__(self):
        import picamera
        import picamera.array

        self.__camera = picamera.PiCamera()

        time.sleep(2)  # Let the camera adjust parameters before disabling auto mode
        awb_gains = self.__camera.awb_gains
        self.__camera.awb_mode = 'off'
        self.__camera.awb_gains = awb_gains
        self.__camera.exposure_mode = 'off'

        self.__camera.resolution = (Config.clients['image_size']['width'], Config.clients['image_size']['height'])
        self.__camera.framerate = Config.clients['frame_rate']
        self.__stream = picamera.array.PiRGBArray(self.__camera, size=(320, 240))
        self.__current_capture_thread = None

        self.__camera.start_preview()
        print('Camera started')

        self.__camera.capture(self.__stream, format='bgr', use_video_port=True)

    def __grab_image(self):
        self.__stream.truncate(0)
        self.__camera.capture(self.__stream, format='bgr', use_video_port=True)

    def grab_image(self):
        try:
            self.__current_capture_thread.join()
        except AttributeError:
            pass

        self.__current_capture_thread = Thread(target=self.__grab_image)
        self.__current_capture_thread.start()
        return self.__stream.array
