from connectivity import client


class VSNClient(client.TCPClient):
    def __init__(self, server_address: str, server_port: int, data_received_callback: callable([object])):
        self.__data_received_callback = data_received_callback

        super().__init__(server_address, server_port)

    def connection_made(self):
        pass

    def data_received(self, received_object: object):
        self.__data_received_callback(received_object)
