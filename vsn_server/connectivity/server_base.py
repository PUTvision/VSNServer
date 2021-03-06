import asyncio
import pickle
from abc import ABCMeta, abstractmethod


class ConnectedClient:
    def __init__(self, writer, loop):
        self.__loop = loop
        self.__writer = writer
        self.__address, self.__port = writer.get_extra_info('peername')
        self.__sending_task = None

        self.id = None

    @property
    def address(self):
        return self.__address

    @property
    def port(self):
        return self.__port

    async def __send(self, obj: object):
        encoded_data = pickle.dumps(obj)
        self.__writer.write(len(encoded_data).to_bytes(4, byteorder='big') +
                            encoded_data)

    def send(self, object_to_send: object):
        self.__sending_task = self.__loop.create_task(self.__send(
            object_to_send))

    def disconnect(self):
        self.__sending_task.cancel()
        self.__writer.close()


class TCPServer(metaclass=ABCMeta):
    def __init__(self, address: str, port: int):
        self.__loop = asyncio.get_event_loop()
        coro = asyncio.start_server(self.__run, address, port, loop=self.__loop)
        self.__server = self.__loop.run_until_complete(coro)

    async def __run(self, reader, writer):
        client = ConnectedClient(writer, self.__loop)
        self.client_connected(client)

        try:
            while True:
                encoded_length = await reader.readexactly(4)
                length = int.from_bytes(encoded_length, byteorder='big')

                pickled_obj = await reader.readexactly(length)
                obj = pickle.loads(pickled_obj)

                self.data_received(client, obj)
        except (asyncio.streams.IncompleteReadError, ConnectionResetError):
            self.client_disconnected(client)

    def stop(self):
        self.__server.close()

    @abstractmethod
    def client_connected(self, client: ConnectedClient):
        ...

    @abstractmethod
    def client_disconnected(self, client: ConnectedClient):
        ...

    @abstractmethod
    def data_received(self, client, received_object: object):
        ...
