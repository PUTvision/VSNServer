from common.VSNUtility import Config


class ConfigurationPacketToClient:
    def __init__(self, node_id=None):
        self.node_id = node_id
        self.hostname_based_ids = Config.clients['hostname_based_ids']
        self.image_size = Config.clients['image_size']
        self.frame_rate = Config.clients['frame_rate']
        self.parameters_below_threshold = Config.clients['parameters_below_threshold']
        self.parameters_above_threshold = Config.clients['parameters_above_threshold']
        self.activation_level_threshold = Config.clients['activation_level_threshold']


class ConfigurationPacketToServer:
    def __init__(self, node_id):
        self.node_id = node_id


class DataPacketToServer:
    def __init__(self, white_pixels, activation_level, flag_image_next, image=None):
        self.white_pixels = white_pixels
        self.activation_level = activation_level
        self.flag_image_next = flag_image_next
        self.image = image

    def set(self, white_pixels, activation_level, flag_image_next, image=None):
        self.white_pixels = white_pixels
        self.activation_level = activation_level
        self.flag_image_next = flag_image_next
        self.image = image


class DataPacketToClient:
    def __init__(self, activation_neighbours, image_type, flag_send_image):
        self.activation_neighbours = activation_neighbours
        self.image_type = image_type
        self.flag_send_image = flag_send_image

    def set(self, activation_neighbours, image_type, flag_send_image):
        self.activation_neighbours = activation_neighbours
        self.image_type = image_type
        self.flag_send_image = flag_send_image


class ClientPacketRouter:
    def __init__(self, data_packet_callback: callable([object]), configuration_packet_callback: callable([object])):
        self.__data_packet_callback = data_packet_callback
        self.__configuration_packet_callback = configuration_packet_callback

    def route_packet(self, packet: object):
        if isinstance(packet, DataPacketToClient):
            self.__data_packet_callback(packet)
        elif isinstance(packet, ConfigurationPacketToClient):
            self.__configuration_packet_callback(packet)
        else:
            raise TypeError('Packet of unsupported type received')


class ServerPacketRouter:
    def __init__(self, data_packet_callback: callable([object, object]),
                 configuration_packet_callback: callable([object, object])):
        self.__data_packet_callback = data_packet_callback
        self.__configuration_packet_callback = configuration_packet_callback

    def route_packet(self, client, packet: object):
        if isinstance(packet, DataPacketToServer):
            self.__data_packet_callback(client, packet)
        elif isinstance(packet, ConfigurationPacketToServer):
            self.__configuration_packet_callback(client, packet)
        else:
            raise TypeError('Packet of unsupported type received')
