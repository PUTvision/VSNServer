__author__ = 'Amin'

import cv2

from threading import Thread
from common.VSNPacket import ImageType

import picamera
import picamera.array
import io
import numpy as np
import time


class VSNImageProcessing:
    def __init__(self, _):
        self._camera = None
        self._structing_element = None
        self._difference_thresholded_image = None
        self._background_image = None
        self._foreground_image = None

        self._init_camera()
        self._stream = picamera.array.PiRGBArray(self._camera, size=(320, 240))
        self._current_frame = None
        self._current_capture_thread = None

        self._grab_new_image_in_opencv_format()

    def _init_camera(self):
        self._camera = picamera.PiCamera()
        self._camera.resolution = (320, 240)
        self._camera.framerate = 20

        print("Frame resolution set")

        self._camera.start_preview()
        # let the camera adjust the auto parameters (gain etc.) on a few images
        time.sleep(2)
        stream = io.BytesIO()
        self._camera.capture(stream, format='jpeg', use_video_port=True)

        print("Camera started")

        data = np.fromstring(stream.getvalue(), dtype=np.uint8)
        frame = cv2.imdecode(data, 1)

        # init all the images with last of the acquired frame
        self._background_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self._foreground_image = self._background_image
        self._difference_thresholded_image = self._background_image

        self._structing_element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

    def grab_images(self, _):
        pass

    def _grab_new_image_in_opencv_format(self):
        self._stream.truncate(0)
        self._camera.capture(self._stream, format='bgr', use_video_port=True)
        self._current_frame = self._stream.array

    def get_image(self, image_type: ImageType):
        if image_type == ImageType.foreground:
            image = self._foreground_image
        elif image_type == ImageType.background:
            image = self._background_image
        else:
            image = self._difference_thresholded_image

        return image

    def get_percentage_of_active_pixels_in_new_frame_from_camera(self):
        # grab and process frame, update the background and foreground model
        # process the frame

        try:
            self._current_capture_thread.join()
        except AttributeError:
            pass

        self._foreground_image = cv2.cvtColor(self._current_frame, cv2.COLOR_BGR2GRAY)

        self._current_capture_thread = Thread(target=self._grab_new_image_in_opencv_format)
        self._current_capture_thread.start()

        # calculate the difference between current and background frame
        difference = cv2.absdiff(self._background_image, self._foreground_image)
        # process the difference
        # use median blur
        blurred = cv2.medianBlur(difference, 3)
        # do the thresholding
        display = cv2.compare(blurred, 6, cv2.CMP_GT)
        # erode and dilate
        eroded = cv2.erode(display, self._structing_element)
        dilated = cv2.dilate(eroded, self._structing_element)
        # store the difference image for further usage
        self._difference_thresholded_image = dilated
        # count non zero elements
        nonzero_pixels = cv2.countNonZero(dilated)
        # calculate the number of non-zero pixels
        height, width = self._foreground_image.shape
        percentage_of_nonzero_pixels = (nonzero_pixels * 100 / (height * width))
        # prepare data for background update
        mask_gt = cv2.compare(self._background_image, self._foreground_image, cv2.CMP_GT)
        mask_lt = cv2.compare(self._background_image, self._foreground_image, cv2.CMP_LT)
        # update the background
        self._background_image += mask_lt / 128.0
        self._background_image -= mask_gt / 128.0

        return percentage_of_nonzero_pixels


if __name__ == "__main__":
    VSN_image_processor = VSNImageProcessing()

    key = 0
    while key != 27:  # exit on ESC
        # main loop - 20 fps
        percentage_of_active_pixels_ = VSN_image_processor.get_percentage_of_active_pixels_in_new_frame_from_camera()
        cv2.imshow("current frame", VSN_image_processor.get_image(ImageType.foreground))
        print("Percentage of of active pixels in the image: ", percentage_of_active_pixels_, "\r\n")
        key = cv2.waitKey(50)

    cv2.destroyAllWindows()
