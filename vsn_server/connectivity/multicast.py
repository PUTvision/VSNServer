import socket
import asyncio


class MulticastServer:
    def __init__(self):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        self.__loop = asyncio.get_event_loop()
        self.__sending_task = self.__loop.call_soon(self.__send)

    def __send(self):
        self.__socket.sendto(bytes(socket.gethostbyname(socket.getfqdn()),
                                   encoding='utf8'), ('255.255.255.255', 54545))
        self.__sending_task = self.__loop.call_later(5, self.__send)

    def stop(self):
        self.__sending_task.cancel()
