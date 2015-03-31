__author__ = 'Amin'

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

import numpy as np

import random

from twisted.protocols import basic
from twisted.internet import protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

from VSNPacket import VSNPacket

from itertools import izip

class SimpleServer(basic.Int32StringReceiver):

    def __init__(self, factory):
        self.factory = factory
        self._packet = VSNPacket()

    # callbacks and functions to override

    def connectionMade(self):
        print "Client connected"
        self.factory.client_connection_made(self)
        #self.transport.write("Welcome! There are currently %d open connections.\n" %(self.factory.numProtocols,))
        #self.sendLine("Welcome! There are currently %d open connections.\n" % self.factory.clients.count())

    def connectionLost(self, reason):
        print "Client disconnected"
        self.factory.client_connection_lost(self)

    def stringReceived(self, string):
        print "Received full msg: " + string
        unpacked_data = self._packet.unpack(string)
        print "Unpacked data: ", unpacked_data
        for i, data_item in enumerate(unpacked_data):
            activation[i] = data_item

    # useful only for LineReceiver protocol
    def lineReceived(self, line):
        print "Line received: " + line
        self.sendLine("Thanks for the message")

    #def dataReceived(self, data):
        #self.transport.write(data)


class SimpleServerFactory(protocol.Factory):

    def __init__(self, quote=None):
        self.clients = []
        self.quote = quote or "My text"

    def buildProtocol(self, addr):
        p = SimpleServer(self)
        return p

    def client_connection_made(self, client):
        self.clients.append(client)

    def client_connection_lost(self, client):
        self.clients.remove(client)


def f(s, reactor):
    print "this will run 3.5 seconds after it was scheduled: %s" % s
    reactor.callLater(2.5, f, s, reactor)

# ## global variables ###
# white pixel percentage
percentage = np.zeros((4, 1))
# current activation level
activation = np.zeros((4, 1))
# current neighbouring nodes activation level
activation_neighbours = np.zeros((4, 1))
# activation level history
activation_history = np.zeros((4, 200))

def update_plot_1():
    global activation, activation_history
    global curve_1, bar_1, cam_plot_1
    global curve_2, bar_2, cam_plot_2
    global curve_3, bar_3, cam_plot_3
    global curve_4, bar_4, cam_plot_4

    curve_1.setData(activation_history[0])
    bar_1.setData([0, 20], percentage[0])

    curve_2.setData(activation_history[1])
    bar_2.setData([0, 20], percentage[1])

    curve_3.setData(activation_history[2])
    bar_3.setData([0, 20], percentage[2])

    curve_4.setData(activation_history[3])
    bar_4.setData([0, 20], percentage[3])

    for idx in range(0, 4):
        activation_history[idx] = np.roll(activation_history[idx], -1)
        activation_history[idx][199] = activation[idx]
        #activation_history[idx][199] = random.randint(1, 100)

# set default background color to white
pg.setConfigOption('background', 'w')
# open the plot window, set properties
win = pg.GraphicsWindow(title="VSN activity monitor")
win.resize(1400, 800)
win.setWindowTitle('VSN activity monitor')

#setup plot 1
cam_plot_1 = win.addPlot(title="picam01")
curve_1 = cam_plot_1.plot(pen='r')
bar_1 = pg.PlotCurveItem([0, 200], [0], stepMode=True, fillLevel=0, brush=(0, 0, 255, 20))
cam_plot_1.addItem(bar_1)
#set the scale of the plot
cam_plot_1.setYRange(0, 100)

#setup plot 2
cam_plot_2 = win.addPlot(title="picam02")
curve_2 = cam_plot_2.plot(pen='r')
bar_2 = pg.PlotCurveItem([0, 200], [0], stepMode=True, fillLevel=0, brush=(0, 0, 255, 20))
cam_plot_2.addItem(bar_2)
#set the scale of the plot
cam_plot_2.setYRange(0, 100)

#next row
win.nextRow()

#setup plot 3
cam_plot_3 = win.addPlot(title="picam03")
curve_3 = cam_plot_3.plot(pen='r')
bar_3 = pg.PlotCurveItem([0, 200], [0], stepMode=True, fillLevel=0, brush=(0, 0, 255, 20))
cam_plot_3.addItem(bar_3)
#set the scale of the plot
cam_plot_3.setYRange(0, 100)

#setup plot 3
cam_plot_4 = win.addPlot(title="picam04")
curve_4 = cam_plot_4.plot(pen='r')
bar_4 = pg.PlotCurveItem([0, 200], [0], stepMode=True, fillLevel=0, brush=(0, 0, 255, 20))
cam_plot_4.addItem(bar_4)
#set the scale of the plot
cam_plot_4.setYRange(0, 100)

timer_plot_1 = QtCore.QTimer()
timer_plot_1.timeout.connect(update_plot_1)
timer_plot_1.start(200)

### connection details ###
TCP_PORT = 50001
endpoint = TCP4ServerEndpoint(reactor, TCP_PORT)
endpoint.listen(SimpleServerFactory())


if __name__ == '__main__':
    QtGui.QApplication.instance().exec_()
    #reactor.callLater(2.5, f, "Hello world!", reactor)
    reactor.run()