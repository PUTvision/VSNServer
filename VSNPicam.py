__author__ = 'Amin'

from VSNClient import VSNClientFactory
from VSNPacket import VSNPacket
from VSNImageProcessing import VSNImageProcessing
from VSNImageProcessing import VSNActivityController

from twisted.internet import reactor

import socket
import cv2
import numpy


class VSNPicam:

    def __init__(self, camera_name=None, video_capture_number=0):
        self._node_name = camera_name
        self._node_number = None
        self._flag_send_image = False           # default behavior - do not send the image data

        self._prepare_camera_name_and_number()

        self._client_factory = VSNClientFactory(self._packet_received_callback)
        self._image_processor = VSNImageProcessing(video_capture_number)
        self._activity_controller = VSNActivityController()
        self._packet_to_send = VSNPacket()

        self._packet_to_send.set(
            self._node_number,
            0.0,
            self._activity_controller.activation_level,
            self._flag_send_image
        )

        self._reactor = None

    def _prepare_camera_name_and_number(self):
        # check the length of the picamXX word - just for testing
        #print 'picamXX length: ', len(self._node_name)

        if self._node_name is None:
            self._node_name = socket.gethostname()
        self._node_number = 0
        if len(self._node_name) == 7 and self._node_name[0:5] == "picam":
            if self._node_name[5:7].isdigit():
                self._node_number = int(self._node_name[5:7])

        print "Node number: ", self._node_number, "\r\n", "Node name: ", self._node_name

    def _do_regular_update(self):
        # queue the next call to itself
        reactor.callLater(self._activity_controller.sample_time, self._do_regular_update)

        percentage_of_nonzero_pixels = self._image_processor.do_image_processing()
        self._activity_controller.update_sensor_state_based_on_captured_image(percentage_of_nonzero_pixels)

        print "Params: " + \
              str(self._activity_controller.activation_level) + \
              ", " + \
              str(self._activity_controller.gain) + \
              ", " +\
              str(self._activity_controller.sample_time) + \
              "\r\n"

        self._packet_to_send.set(
            self._node_number,
            percentage_of_nonzero_pixels,
            self._activity_controller.activation_level,
            self._flag_send_image
        )
        self._client_factory.send_packet(self._packet_to_send)

        # encode image for sending
        if self._flag_send_image:
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
            result, imgencode = cv2.imencode('.jpg', self._image_processor._background_image, encode_param)
            data = numpy.array(imgencode)
            image_as_string = data.tostring()
            self._client_factory.send_image(image_as_string)

    def _packet_received_callback(self, packet):
        print "Received packet: ", packet.activation_neighbours, ", ", packet.image_type
        self._activity_controller.set_params(packet.activation_neighbours)
        self._flag_send_image = packet.flag_send_image
        # TODO: add a field for storing which image should be sent

    def start(self, server_ip="127.0.0.1", server_port=50001):
        # connect factory to this host and port
        reactor.connectTCP(server_ip, server_port, self._client_factory)
        reactor.callLater(self._activity_controller.sample_time, self._do_regular_update)

        reactor.run()

if __name__ == '__main__':
    picam = VSNPicam("picam01", 0)

    picam.start()
