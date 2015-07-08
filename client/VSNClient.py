__author__ = 'Amin'

from twisted.protocols import basic
from twisted.internet import protocol
from twisted.internet import reactor

from common.VSNPacket import VSNPacketToClient


class VSNClient(basic.Int32StringReceiver):
    def __init__(self):
        pass

    # callbacks and functions to override

    def connectionMade(self):
        print("Connected to server")
        self.factory.client_connected(self)

    def connectionLost(self, reason):
        print("Disconnected from server" + str(reason))
        self.factory.client_disconnected()

    def stringReceived(self, string):
        packet = VSNPacketToClient.deserialize(string)
        self.factory.client_received_data(packet)

    # additional functions

    def send_packet(self, packet):
        data_packed_as_string = packet.serialize()
        self.sendString(data_packed_as_string)

    def send_image(self, image_as_string):
        self.sendString(image_as_string)


class VSNClientFactory(protocol.ClientFactory):
    protocol = VSNClient
    # above line is equal to
    # def buildProtocol(self, addr):
    #     p = SimpleClient()
    #     p.factory = self
    #     return p

    def __init__(self, packet_received_callback):
        self.client = None
        self._packet_received_callback = packet_received_callback

    def clientConnectionLost(self, connector, reason):
        print("Disconnected, trying to reconnect")
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print("Connection failed:", reason)
        reactor.stop()

    def client_connected(self, client):
        self.client = client

    def client_disconnected(self):
        self.client = None

    def client_received_data(self, packet):
        self._packet_received_callback(packet)

    def send_packet(self, packet):
        if self.client:
            self.client.send_packet(packet)

    def send_image(self, image_as_string):
        if self.client:
            self.client.send_image(image_as_string)


from twisted.internet import task
from common.VSNPacket import VSNPacketToServer


def send_packet(packet):
    client_factory.send_packet(packet)


def packet_receive_callback(packet):
    print("Received packet: " +
          str(packet.activation_neighbours) + ", " +
          str(packet.image_type) + ", " +
          str(packet.flag_send_image) + "\r\n")

if __name__ == '__main__':
    SERVER_IP = '127.0.0.1'
    SERVER_PORT = 50001

    # create factory protocol and application
    client_factory = VSNClientFactory(packet_receive_callback)

    # connect factory to this host and port
    reactor.connectTCP(SERVER_IP, SERVER_PORT, client_factory)

    VSN_packet = VSNPacketToServer(1, 10.0, 5.0, False)
    periodic_action = task.LoopingCall(send_packet, VSN_packet)
    periodic_action.start(2.0)

    reactor.run()
