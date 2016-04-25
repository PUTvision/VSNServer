import logging
from enum import Enum
from typing import Any, Dict

from vsn_server.connectivity.packets import ConfigurationPacket
from vsn_server.connectivity.router import PacketRouter
from vsn_server.connectivity import server_base
from vsn_server.processing.reactor import Reactor


class ReceiveState(Enum):
    packet_standard = 1
    packet_image = 2


class Server(server_base.TCPServer):
    def __init__(self, address: str, port: int, reactor: Reactor):
        self.__clients = []

        self.__reactor = reactor
        self.__packet_router = PacketRouter(self.__reactor)

        super().__init__(address, port)

    def send_to_all_clients(self, obj: object):
        for client in self.__clients:
            client.send(obj)

    async def client_connected(self, client: server_base.ConnectedClient):
        logging.info('New client connecting...')

        await client.send(ConfigurationPacket())
        logging.debug('Configuration packet sent')

        self.__clients.append(client)

    async def client_disconnected(self, client: server_base.ConnectedClient,
                                  future):
        logging.info('Client {} disconnected'.format(client.id))

        self.__clients.remove(client)

    async def data_received(self, client, received_object: Dict[str, Any]):
        self.__packet_router.route_packet(client, received_object)
