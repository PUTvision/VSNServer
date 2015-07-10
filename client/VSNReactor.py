import asyncio

import socket
import cv2
import numpy
import time

from client.VSNImageProcessor import VSNImageProcessor
from client.VSNActivityController import VSNActivityController
from common.VSNPacket import DataPacketToServer, ClientPacketRouter, ConfigurationPacketToServer

from client.VSNClient import VSNClient
from common.VSNUtility import ImageType, Config


class VSNReactor:
    def __init__(self, camera):
        self.__node_id = None
        self.__camera = camera
        self.__flag_send_image = False  # default behavior - do not send the image data
        self.__image_type = ImageType.foreground

        self.__client = VSNClient(Config.server['address'],
                                  Config.server['listening_port'],
                                  ClientPacketRouter(self.__process_data_packet, self.__process_configuration_packet))

        self.__image_processor = VSNImageProcessor(camera.grab_image())
        self.__activity_controller = None

        self.__do_regular_update_time = 0

        self.__event_loop = asyncio.get_event_loop()

        self.__waiting_for_configuration = False

    def __do_regular_update(self):
        current_time = time.perf_counter()
        print('\nPREVIOUS REGULAR UPDATE WAS %.2f ms AGO' % ((current_time - self.__do_regular_update_time) * 1000))
        self.__do_regular_update_time = current_time
        # queue the next call to itself
        self.__event_loop.call_later(self.__activity_controller.get_sample_time(), self.__do_regular_update)

        time_start = time.perf_counter()

        percentage_of_active_pixels = self.__image_processor.get_percentage_of_active_pixels_in_frame(
            self.__camera.grab_image())
        self.__activity_controller.update_sensor_state_based_on_captured_image(percentage_of_active_pixels)

        time_after_get_percentage = time.perf_counter()

        print(self.__activity_controller.get_state_as_string())

        if self.__flag_send_image:
            image_as_string = self.__encode_image_for_sending()
        else:
            image_as_string = None

        time_after_encoding = time.perf_counter()

        self.__client.send(DataPacketToServer(percentage_of_active_pixels,
                                              self.__activity_controller.get_activation_level(),
                                              self.__flag_send_image,
                                              image_as_string))

        time_after_sending_packet = time.perf_counter()

        print('Calculating percentage took: %.2f ms' % ((time_after_get_percentage - time_start) * 1000))
        print('Encoding took: %.2f ms' % ((time_after_encoding - time_after_get_percentage) * 1000))
        print('Sending packet took: %.2f ms' % ((time_after_sending_packet - time_after_encoding) * 1000))

    def __encode_image_for_sending(self):
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        image_to_send = self.__image_processor.get_image(self.__image_type)
        result, image_encoded = cv2.imencode('.jpg', image_to_send, encode_param)
        data = numpy.array(image_encoded)
        image_as_string = data.tostring()
        return image_as_string

    def __process_data_packet(self, packet):
        print('Received data packet: ', packet.activation_neighbours, ',', packet.flag_send_image)

        self.__activity_controller.set_params(
            activation_neighbours=packet.activation_neighbours
        )
        self.__flag_send_image = packet.flag_send_image

    def __process_configuration_packet(self, packet):
        print('Received configuration packet: %r %r %r' % (packet.node_id, packet.parameters_below_threshold,
                                                           packet.parameters_above_threshold))

        self.__image_type = packet.image_type

        self.__activity_controller = VSNActivityController(packet.parameters_below_threshold,
                                                           packet.parameters_above_threshold,
                                                           packet.activation_level_threshold)

        if packet.node_id is not None:
            # First configuration packet with node_id
            self.__node_id = packet.node_id
        elif self.__node_id is None and packet.hostname_based_ids:
            # First configuration packet without node_id
            try:
                self.__node_id = int(''.join(x for x in socket.gethostname() if x.isdigit()))
                self.__client.send(ConfigurationPacketToServer(self.__node_id))
            except ValueError:
                print('Client hostname does not provide camera number - exiting')
                self.__event_loop.stop()

        if self.__waiting_for_configuration:
            self.start()

    def start(self):
        if self.__node_id is not None:
            self.__event_loop.call_later(self.__activity_controller.get_sample_time(), self.__do_regular_update)
        else:
            self.__waiting_for_configuration = True

        if not self.__event_loop.is_running():
            self.__event_loop.run_forever()
