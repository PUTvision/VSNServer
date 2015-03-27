__author__ = 'Amin'
from twisted.internet import protocol
from twisted.internet import reactor
from twisted.internet import task


class SimpleClient(protocol.Protocol):

    def __init__(self):
        # parameters
        self._private_parameter = 0
        self.periodic_action = []

    def connectionMade(self):
        print "Connected to server"
        self.transport.write("Hello server, I am the client!\r\n")
        self.periodic_action = task.LoopingCall(self.send_message, "asdasd")
        self.periodic_action.start(2.0)

    def dataReceived(self, data):
        print "Data received: " + data

    def send_message(self, msg):
        self.transport.write("MESSAGE %s\r\n" % msg)


class SimpleClientFactory(protocol.ClientFactory):

    def __init__(self):
        self._common_parameter = 0

    def buildProtocol(self, addr):
        p = SimpleClient()
        p.factory = self
        return p

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