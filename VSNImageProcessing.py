__author__ = 'Amin'

import cv2
import cv2.cv as cv


class VSNImageProcessing:

    def __init__(self):

        self._capture = None
        self._struct = None
        self._background_image = None
        self._foreground_image = None

        self.init_camera()

    def init_camera(self):
        self._capture = cv2.VideoCapture(0)
        self._capture.set(cv.CV_CAP_PROP_FRAME_WIDTH, 320)
        self._capture.set(cv.CV_CAP_PROP_FRAME_HEIGHT, 240)

        print "Frame resolution set to: (" +\
              str(self._capture.get(cv.CV_CAP_PROP_FRAME_WIDTH)) + \
              "; " + \
              str(self._capture.get(cv.CV_CAP_PROP_FRAME_HEIGHT)) + \
              ")"

        # let the camera adjust the auto parameters (gain etc.) on a few images
        for x in xrange(0, 15):
            ret, frame = self._capture.read()
        self._background_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self._struct = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

    def do_image_processing(self):
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
        eroded = cv2.erode(display, self._struct)
        dilated = cv2.dilate(eroded, self._struct)
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

import math


class VSNActivityController:

    def __init__(self):
        self.filename = "log.csv"            # log file name - if logging is enabled
        self.activation_level = 0            # default starting activation level
        self.sample_time = 0.1               # sample time at startup
        self.gain = 0.1                      # gain at startup
        self.flag_senddata = False           # default behavior - do not send the image data
        self.activation_neighbours = 0       # weighted activity of neighbouring nodes

    # lowpass filter function modelled after a 1st order inertial object transformed using delta minus method
    def lowpass(self, prev_sample, current_sample, sample_time):
        time_constant = 1
        output = \
            (self.gain / time_constant) * current_sample + \
            prev_sample * pow(math.e, -1.0 * (sample_time / time_constant))
        return output

    def set_params(self, activation_neighbours):
        self.activation_neighbours = activation_neighbours

    def update_sensor_state_based_on_captured_image(self, percentage_of_nonzero_pixels):
        # compute the sensor state based on captured images
        activation_level_new = self.lowpass(
            self.activation_level,
            percentage_of_nonzero_pixels,
            self.sample_time
        )
        self.activation_level = activation_level_new + self.activation_neighbours

        # update sampling time and gain based on current activity level
        if self.activation_level < 10:
            self.sample_time = 1
            self.gain = 2
        else:
            self.sample_time = 0.1
            self.gain = 0.1

    def prepare_data_to_send(self):
        #TODO: implement function that gathers all the data (also choosen image) and packs it for sending
        print "Not implemented yet"


if __name__ == "__main__":
    VSN_image_processor = VSNImageProcessing()
    VSN_activity_controller = VSNActivityController()

    while True:

        # main loop
        key = cv2.waitKey(50)
        if key == 27:  # exit on ESC
            break
        percentage_of_nonzero_pixels = VSN_image_processor.do_image_processing()
        VSN_activity_controller.update_sensor_state_based_on_captured_image(percentage_of_nonzero_pixels)
        cv2.imshow('fg', VSN_image_processor._background_image)
        print "Params: " + \
              str(VSN_activity_controller.activation_level) + \
              ", " + \
              str(VSN_activity_controller.gain) + \
              ", " +\
              str(VSN_activity_controller.sample_time) + \
              "\r\n"

    cv2.destroyAllWindows()