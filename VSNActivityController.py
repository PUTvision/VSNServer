__author__ = 'Amin'

import math


class VSNActivityController:

    def __init__(self):
        self.filename = "log.csv"            # log file name - if logging is enabled
        self.activation_level = 0.0          # default starting activation level
        self.sample_time = 1.0               # sample time at startup
        self.gain = 0.1                      # gain at startup
        self.activation_neighbours = 0.0     # weighted activity of neighbouring nodes

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
            self.gain = 0.1
        else:
            self.sample_time = 0.1
            self.gain = 0.1