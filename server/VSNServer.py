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

    def client_connected(self, client: server.ConnectedClient):
        client.id = self.__find_free_id()
        self.__clients.append(client)
        self.__client_connected_callback(client)

    def client_disconnected(self, client: server.ConnectedClient):
        self.__free_id(client.id)
        self.__clients.remove(client)
        self.__client_disconnected_callback()

    def data_received(self, client, received_object: object):
        self.__data_received_callback(client, received_object)
