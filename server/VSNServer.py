from enum import Enum

from connectivity import server
from common.VSNUtility import Config


class ReceiveState(Enum):
    packet_standard = 1
    packet_image = 2


class VSNServer(server.TCPServer):
    def __init__(self, address: str, port: int,
                 client_connected_callback: callable([]),
                 client_disconnected_callback: callable([]),
                 no_clients_left_callback: callable([]),
                 packet_router):
        self.__clients = []
        self.__client_connected_callback = client_connected_callback
        self.__client_disconnected_callback = client_disconnected_callback
        self.__no_clients_left_callback = no_clients_left_callback
        self.__packet_router = packet_router

        self.__first_free_id = 1
        self.__ids_in_use = set()

        super().__init__(address, port)

    def __find_free_id(self):
        id_to_return = self.__first_free_id
        self.__ids_in_use.add(id_to_return)
        self.__first_free_id += 1

        while self.__first_free_id in self.__ids_in_use:
            self.__first_free_id += 1

        return id_to_return

    def __free_id(self, client_id: int):
        self.__ids_in_use.remove(client_id)

        if client_id < self.__first_free_id:
            self.__first_free_id = client_id

    def send_to_all_clients(self, obj: object):
        for client in self.__clients:
            client.send(obj)

    def client_connected(self, client: server.ConnectedClient):
        if not Config.clients['hostname_based_ids']:
            client.id = self.__find_free_id()

        self.__clients.append(client)
        self.__client_connected_callback(client)

    def client_disconnected(self, client: server.ConnectedClient):
        if not Config.clients['hostname_based_ids']:
            self.__free_id(client.id)

        self.__clients.remove(client)
        self.__client_disconnected_callback(client)

        if len(self.__clients) == 0:
            self.__no_clients_left_callback()

    def data_received(self, client, received_object: object):
        self.__packet_router.route_packet(client, received_object)
