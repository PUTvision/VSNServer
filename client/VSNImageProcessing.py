__author__ = 'Amin'

import cv2
import cv2.cv as cv

from common.VSNPacket import IMAGE_TYPES


class VSNImageProcessing:

    def __init__(self, video_capture_number=0):
        self._capture = None
        self._structing_element = None
        self._difference_thresholded_image = None
        self._background_image = None
        self._foreground_image = None

        self._init_camera(video_capture_number)

    def _init_camera(self, video_capture_number):
        self._capture = cv2.VideoCapture(video_capture_number)
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
        if ret:
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
            percentage_of_nonzero_pixels = (nonzero_pixels * 100.0 / (height * width))
            # prepare data for background update
            mask_gt = cv2.compare(self._background_image, self._foreground_image, cv2.CMP_GT)
            mask_lt = cv2.compare(self._background_image, self._foreground_image, cv2.CMP_LT)
            # update the background
            self._background_image += mask_lt / 128.0
            self._background_image -= mask_gt / 128.0
        else:
            percentage_of_nonzero_pixels = 0

        return percentage_of_nonzero_pixels

    # helper function used to flush the camera buffer
    def grab_images(self, number_of_images_to_grab):
        for i in xrange(0, number_of_images_to_grab):
            self._capture.read()


if __name__ == "__main__":
    VSN_image_processor = VSNImageProcessing()

    key = 0
    while key != 27:    # exit on ESC
        # main loop - 20 fps
        percentage_of_active_pixels_ = VSN_image_processor.get_percentage_of_active_pixels_in_new_frame_from_camera()
        cv2.imshow("current frame", VSN_image_processor.get_image(IMAGE_TYPES.foreground))
        print "Percentage of of active pixels in the image: ", percentage_of_active_pixels_, "\r\n"
        key = cv2.waitKey(50)

    cv2.destroyAllWindows()