__author__ = 'Amin'

import math


class GainSampletimeTuple:

    def __init__(self, gain, sample_time):
        self.gain = gain
        self.sample_time = sample_time


class VSNActivityController:

    def __init__(self):

        self._parameters_below_threshold = GainSampletimeTuple(2.0, 1.0)
        self._parameters_above_threshold = GainSampletimeTuple(0.1, 0.1)
        self._activation_level_threshold = 10.0

        self._percentage_of_active_pixels = 0.0
        self._activation_level = 0.0                                # default starting activation level
        self._parameters = self._parameters_below_threshold         # sample time and gain at startup
        self._activation_neighbours = 0.0                           # weighted activity of neighbouring nodes

    # lowpass filter function modelled after a 1st order inertial object transformed using delta minus method
    def _lowpass(self, prev_state, input_data):
        time_constant = 1.0
        output = \
            (self._parameters.gain / time_constant) * input_data + \
            prev_state * pow(math.e, -1.0 * (self._parameters.sample_time / time_constant))
        return output

    def set_params(self,
                   activation_neighbours=None,
                   activation_level_threshold=None,
                   parameters_below_threshold=None,
                   parameters_above_threshold=None):
        if activation_neighbours is not None:
            self._activation_neighbours = activation_neighbours
        if activation_level_threshold is not None:
            self._activation_level_threshold = activation_level_threshold
        if parameters_below_threshold is not None:
            self._parameters_below_threshold = parameters_below_threshold
        if parameters_above_threshold is not None:
            self._parameters_above_threshold = parameters_above_threshold

    def get_sample_time(self):
        return self._parameters.sample_time

    def get_percentage_of_active_pixels(self):
        return self._percentage_of_active_pixels

    def get_activation_level(self):
        return self._activation_level

    def is_activation_below_threshold(self):
        result = False
        if self._activation_level < self._activation_level_threshold:
            result = True
        return result

    def update_sensor_state_based_on_captured_image(self, percentage_of_active_pixels):
        # store the incoming data
        self._percentage_of_active_pixels = percentage_of_active_pixels
        # compute the sensor state based on captured images
        activation_level_updated = self._lowpass(
            self._activation_level,
            percentage_of_active_pixels + self._activation_neighbours,
        )
        #self._activation_level = activation_level_updated + self._activation_neighbours
        self._activation_level = activation_level_updated

        # update sampling time and gain based on current activity level
        if self._activation_level < self._activation_level_threshold:
            self._parameters = self._parameters_below_threshold
        else:
            self._parameters = self._parameters_above_threshold

    def get_state_as_string(self):
        return "Params: \r\n" + \
               "% of active pixels: " + \
               str(self._percentage_of_active_pixels) + \
               ", activation level: " + \
               str(self._activation_level) + \
               ", gain: " + \
               str(self._parameters.gain) + \
               ", sample time: " + \
               str(self._parameters.sample_time)


from common.VSNPacket import IMAGE_TYPES
from client.VSNImageProcessing import VSNImageProcessing
import cv2

if __name__ == "__main__":
    VSN_activity_controller = VSNActivityController()
    VSN_image_processor = VSNImageProcessing()

    key = 0
    while key != 27:    # exit on ESC
        # main loop
        key = cv2.waitKey(int(VSN_activity_controller.get_sample_time()*1000))
        percentage_of_active_pixels_ = VSN_image_processor.get_percentage_of_active_pixels_in_new_frame_from_camera()
        VSN_activity_controller.update_sensor_state_based_on_captured_image(percentage_of_active_pixels_)
        cv2.imshow('current frame', VSN_image_processor.get_image(IMAGE_TYPES.foreground))
        print VSN_activity_controller.get_state_as_string()

    cv2.destroyAllWindows()