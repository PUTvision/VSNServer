__author__ = 'Amin'

import cv2
import cv2.cv as cv

from VSNPacket import IMAGE_TYPES


class VSNImageProcessing:

    def __init__(self, video_capture_number=0):

        self._video_capture_number = video_capture_number

        self._capture = None
        self._structing_element = None
        self._difference_thresholded_image = None
        self._background_image = None
        self._foreground_image = None

        self._init_camera()

    def _init_camera(self):
        self._capture = cv2.VideoCapture(self._video_capture_number)
        self._capture.set(cv.CV_CAP_PROP_FRAME_WIDTH, 320)
        self._capture.set(cv.CV_CAP_PROP_FRAME_HEIGHT, 240)

        print "Frame resolution set to: (" +\
              str(self._capture.get(cv.CV_CAP_PROP_FRAME_WIDTH)) + \
              "; " + \
              str(self._capture.get(cv.CV_CAP_PROP_FRAME_HEIGHT)) + \
              ")"

        frame = None
        # let the camera adjust the auto parameters (gain etc.) on a few images
        for x in xrange(0, 15):
            ret, frame = self._capture.read()
        # init all the images with last of the acquired frame
        self._background_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self._foreground_image = self._background_image
        self._difference_image = self._background_image

        self._structing_element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

    def get_image(self, image_type):
        image = None
        if image_type == IMAGE_TYPES.foreground:
            image = self._foreground_image
        elif image_type == IMAGE_TYPES.background:
            image = self._background_image
        else:
            image = self._difference_image

        return image

    def get_percentage_of_active_pixels_in_new_frame_from_camera(self):
        # grab and process frame, update the background and foreground model
        ret, frame = self._capture.read()
        # process the frame
        self._foreground_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
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

from VSNActivityController import VSNActivityController


if __name__ == "__main__":
    VSN_image_processor = VSNImageProcessing()
    VSN_activity_controller = VSNActivityController()

    while True:

        # main loop
        key = cv2.waitKey(int(VSN_activity_controller.get_sample_time()*1000.0))
        if key == 27:  # exit on ESC
            break
        percentage_of_active_pixels_ = VSN_image_processor.get_percentage_of_active_pixels_in_new_frame_from_camera()
        VSN_activity_controller.update_sensor_state_based_on_captured_image(percentage_of_active_pixels_)
        cv2.imshow('current frame', VSN_image_processor.get_image(IMAGE_TYPES.foreground))
        print VSN_activity_controller.get_state_as_string()

    cv2.destroyAllWindows()