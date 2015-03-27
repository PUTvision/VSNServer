__author__ = 'Amin'

from twisted.protocols.basic import LineReceiver
from twisted.internet import protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor


class SimpleServer(LineReceiver):

    def __init__(self):
        self.factory = []

    def connectionMade(self):
        print "Client connected"
        self.factory.numProtocols += 1
        #self.transport.write("Welcome! There are currently %d open connections.\n" %(self.factory.numProtocols,))
        self.sendLine("Welcome! There are currently %d open connections.\n" % self.factory.numProtocols)

    def connectionLost(self, reason):
        print "Client disconnected"
        self.factory.numProtocols -= 1

    def lineReceived(self, line):
        print "Line received: " + line
        self.sendLine("Thanks for the message")

    #def dataReceived(self, data):
        #self.transport.write(data)


class SimpleServerFactory(protocol.Factory):

    def __init__(self, quote=None):
        self.clients = []
        self.numProtocols = 0
        self.quote = quote or "My text"

    def buildProtocol(self, addr):
        p = SimpleServer()
        p.factory = self
        return SimpleServer()

    def clientCo



def f(s, reactor):
    print "this will run 3.5 seconds after it was scheduled: %s" % s
    reactor.callLater(2.5, f, s, reactor)

### connection details ###
TCP_PORT = 50001
endpoint = TCP4ServerEndpoint(reactor, TCP_PORT)
endpoint.listen(SimpleServerFactory())
reactor.callLater(2.5, f, "Hello world!", reactor)
reactor.run()
