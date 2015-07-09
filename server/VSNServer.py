from enum import Enum

from connectivity import server


class ReceiveState(Enum):
    packet_standard = 1
    packet_image = 2


class VSNServer(server.TCPServer):
    def __init__(self, address: str, port: int,
                 client_connected_callback: callable([]),
                 client_disconnected_callback: callable([]),
                 data_received_callback: callable([server.ConnectedClient, object])):
        self.__clients = []
        self.__client_connected_callback = client_connected_callback
        self.__client_disconnected_callback = client_disconnected_callback
        self.__data_received_callback = data_received_callback

        super().__init__(address, port)

    def client_connected(self, client: server.ConnectedClient):
        self.__clients.append(client)
        self.__client_connected_callback()

    def client_disconnected(self, client: server.ConnectedClient):
        self.__clients.remove(client)
        self.__client_disconnected_callback()

    def data_received(self, client, received_object: object):
        self.__data_received_callback(client, received_object)
