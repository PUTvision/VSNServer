import logging

import asyncio
import numpy as np

from vsn_server.connectivity.packets import DataPacket
from vsn_server.common.utility import CameraStatisticsTuple
from vsn_server.ui.graph import GraphController


class Reactor:
    def __init__(self, manager):
        self.__loop = asyncio.get_event_loop()
        self.__graphs_controller = GraphController()
        self.__manager = manager

    def handle_data_packet(self, client, packet):
        logging.debug('Data received from client {}'.format(client.id))

        activation_level = packet['activation_level']
        white_pixels = packet['white_pixels']

        activation_neighbours = self.__manager.update_camera_state(
            client.id,
            activation_level,
            white_pixels
        )

        task = self.__loop.create_task(client.send(
            DataPacket(activation_neighbours))
        )

        self.__graphs_controller.set_new_values(
            client.id,
            activation_level + activation_neighbours,
            white_pixels
        )

        if packet['image'] is not None:
            image_data = np.fromstring(packet['image'], dtype='uint8')
            # decoded_image = cv2.imdecode(image_data, cv2.IMREAD_GRAYSCALE)
            decoded_image = None
            self.__manager.cameras[client.id].set_frame(decoded_image)

        asyncio.wait(task)

    def handle_conf_packet(self, client, packet):
        client.id = packet['node_id']
        logging.info('Client `{}` connected'.format(client.id))

        self.__manager.add_camera(client)
