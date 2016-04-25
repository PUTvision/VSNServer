from vsn_server.common.utility import Config


class ConfigurationPacket(dict):
    def __init__(self, node_id: int=None, send_image=None, image_type=None):
        super().__init__()

        self['_pktype'] = 'clconf'
        self['node_id'] = node_id
        self['image_type'] = image_type
        self['send_image'] = send_image
        self['image_size'] = Config['clients']['image_size']
        self['frame_rate'] = Config['clients']['frame_rate']
        self['parameters_below_threshold'] = Config['clients'][
            'parameters_below_threshold']
        self['parameters_above_threshold'] = Config['clients'][
            'parameters_above_threshold']
        self['activation_threshold'] = Config['clients'][
            'activation_threshold']


class DataPacket(dict):
    def __init__(self, activation_neighbours):
        super().__init__()

        self['_pktype'] = 'cldata'
        self['activation_neighbours'] = activation_neighbours
