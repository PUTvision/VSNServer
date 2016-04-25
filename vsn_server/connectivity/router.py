from typing import Dict, Any

from vsn_server.processing.reactor import Reactor


class PacketRouter:
    def __init__(self, reactor: Reactor):
        self.__reactor = reactor

    def route_packet(self, client, packet: Dict[str, Any]):
        if packet['_pktype'] == 'svdata':
            self.__reactor.handle_data_packet(client, packet)
        elif packet['_pktype'] == 'svconf':
            self.__reactor.handle_conf_packet(client, packet)
        else:
            raise TypeError('Packet of unsupported type received')
