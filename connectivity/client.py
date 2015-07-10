import asyncio
import pickle

from abc import ABCMeta, abstractmethod


class TCPClient(metaclass=ABCMeta):
    def __init__(self, server_address: str, server_port: int):
        self.reader, self.writer = None, None
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.__connect(server_address, server_port))
        self.loop.create_task(self.__receive())

    def __del__(self):
        if self.writer is not None:
            self.disconnect()

    @asyncio.coroutine
    def __connect(self, address: str, port: int):
        self.reader, self.writer = yield from asyncio.open_connection(address, port, loop=self.loop)
        self.connection_made()

    @asyncio.coroutine
    def __send(self, obj: object):
        encoded_data = pickle.dumps(obj)
        self.writer.write(len(encoded_data).to_bytes(4, byteorder='big') + encoded_data)

    @asyncio.coroutine
    def __receive(self):
        while True:
            encoded_length = yield from self.reader.readexactly(4)
            length = int.from_bytes(encoded_length, byteorder='big')

            pickled_obj = yield from self.reader.readexactly(length)
            obj = pickle.loads(pickled_obj)
            self.data_received(obj)

    def send(self, object_to_send: object):
        self.loop.create_task(self.__send(object_to_send))

    def disconnect(self):
        self.writer.close()

    @abstractmethod
    def connection_made(self):
        ...

    @abstractmethod
    def data_received(self, received_object: object):
        ...
