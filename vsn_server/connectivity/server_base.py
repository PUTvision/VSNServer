import asyncio
import functools
from abc import ABCMeta, abstractmethod
from typing import Dict, Any

import msgpack


class ConnectedClient:
    def __init__(self, writer, loop):
        self.__loop = loop
        self.__writer = writer
        self.__address, self.__port = writer.get_extra_info('peername')

        self.id = None

    @property
    def address(self):
        return self.__address

    @property
    def port(self):
        return self.__port

    async def send(self, object_to_send: object):
        encoded_data = msgpack.packb(object_to_send, use_bin_type=True)
        self.__writer.write(len(encoded_data).to_bytes(4, byteorder='big') +
                            encoded_data)
        await self.__writer.drain()

    def disconnect(self):
        self.__writer.close()


class TCPServer(metaclass=ABCMeta):
    def __init__(self, address: str, port: int):
        self.__loop = asyncio.get_event_loop()
        self.__server = self.__loop.run_until_complete(
            asyncio.streams.start_server(self._accept_client, address, port,
                                         loop=self.__loop)
        )
        self.__clients = {}

    async def _accept_client(self, reader, writer):
        client = ConnectedClient(writer, self.__loop)

        task = self.__loop.create_task(self._handle_client(client, reader))
        task.add_done_callback(functools.partial(self.client_disconnected,
                                                 client))

        await self.client_connected(client)

    async def _handle_client(self, client: ConnectedClient, reader):
        while True:
            encoded_length = await reader.readexactly(4)
            length = int.from_bytes(encoded_length, byteorder='big')

            obj = msgpack.unpackb(await reader.readexactly(length),
                                  encoding='utf-8')
            await self.data_received(client, obj)

    def stop(self):
        self.__server.close()
        self.__loop.run_until_complete(self.__server.wait_closed())

    @abstractmethod
    async def client_connected(self, client: ConnectedClient):
        ...

    @abstractmethod
    async def client_disconnected(self, client: ConnectedClient, future):
        ...

    @abstractmethod
    async def data_received(self, client, received_object: Dict[str, Any]):
        ...
