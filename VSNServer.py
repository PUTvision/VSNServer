__author__ = 'Amin'

from twisted.protocols import basic
from twisted.internet import protocol

from VSNPacket import VSNPacket


class VSNServer(basic.Int32StringReceiver):

    def __init__(self):
        # parameters
        self.name = "picamXX"
        self.white_pixels = 0.0
        self.activation_level = 0.0

    # callbacks and functions to override

    def connectionMade(self):
        self.factory.client_connection_made(self)

    def connectionLost(self, reason):
        self.factory.client_connection_lost(self)

    def stringReceived(self, string):
        packet = VSNPacket()
        packet.unpack_from_receive(string)
        self.factory.client_packet_received(packet)

    # additional functions

    def send_packet(self, packet):
        data_packed_as_string = packet.pack_to_send()
        self.sendString(data_packed_as_string)


class VSNServerFactory(protocol.Factory):

    protocol = VSNServer

    def __init__(
            self,
            client_connection_made_callback,
            client_connection_lost_callback,
            client_data_received_callback
    ):
        self.clients = []
        self.client_connection_made_callback = client_connection_made_callback
        self.client_connection_lost_callback = client_connection_lost_callback
        self.client_packet_received = client_data_received_callback

    def buildProtocol(self, addr):
        p = VSNServer()
        p.factory = self
        return p

    def client_connection_made(self, client):
        self.clients.append(client)
        self.client_connection_made_callback()

    def client_connection_lost(self, client):
        self.clients.remove(client)
        self.client_connection_lost_callback()

    def client_packet_received(self, packet):
        self.data_received_callback(packet)

    def send_packet_to_all_clients(self, packet):
        for client in self.clients:
            client.send_packet(packet)