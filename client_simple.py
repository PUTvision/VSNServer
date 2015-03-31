__author__ = 'Amin'
from twisted.protocols import basic
from twisted.internet import protocol
from twisted.internet import reactor
from twisted.internet import task

import random

from VSNPacket import VSNPacket


class SimpleClient(basic.Int32StringReceiver):

    def __init__(self):
        # parameters
        self._private_parameter = 0
        self.periodic_action = []
        self.packet = VSNPacket()


    # callbacks and functions to override

    def connectionMade(self):
        print "Connected to server"
        #self.example_basic_send("Hello server, I am the client!\r\n")

        packed_data = self.packet.pack(
            random.randint(0, 100),
            random.randint(0, 100),
            random.randint(0, 100),
            random.randint(0, 100)
        )
        self.periodic_action = task.LoopingCall(self.send_int32string_msg, packed_data)
        #self.periodic_action = task.LoopingCall(self.send_int32string_msg, "asidhkqwe mnbn")
        self.periodic_action.start(2.0)

    def connectionLost(self, reason):
        print "Disconnected from server"
        self.periodic_action.stop()

    def stringReceived(self, string):
        print "Received full msg: " + string

    def dataReceived(self, data):
        print "Data received: " + data

    # example and additional functions

    def send_int32string_msg(self, string):
        print "Sending int32string msg: " + string
        self.sendString(string)

    def example_basic_send(self, msg):
        self.transport.write("MESSAGE %s\r\n" % msg)


class SimpleClientFactory(protocol.ClientFactory):

    protocol = SimpleClient
    # above line is equal to
    #def buildProtocol(self, addr):
    #    p = SimpleClient()
    #    p.factory = self
    #    return p

    def __init__(self):
        self._common_parameter = 0

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        print "Disconnected, trying to reconnect"
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()

if __name__ == '__main__':
    # initialize logging
    #log.startLogging(sys.stdout)

    # constant definitions
    #SERVER_IP = '192.168.0.100'
    SERVER_IP = '127.0.0.1'
    SERVER_PORT = 50001

    # create factory protocol and application
    client_factory = SimpleClientFactory()

    # connect factory to this host and port
    reactor.connectTCP(SERVER_IP, SERVER_PORT, client_factory)

    # run bot
    reactor.run()