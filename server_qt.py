__author__ = 'Amin'


from twisted.protocols import basic
from twisted.internet import protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
#from twisted.internet import reactor

from VSNPacket import VSNPacket

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys
import time

import qt4reactor

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

import numpy as np

import random


class SimpleServer(basic.Int32StringReceiver):

    def __init__(self, factory):
        self._factory = factory
        self._packet = VSNPacket()

        self.white_pixels = 0.0
        self.activation_level = 0.0

    # callbacks and functions to override

    def connectionMade(self):
        self._factory.client_connection_made(self)

    def connectionLost(self, reason):
        self._factory.client_connection_lost(self)

    def stringReceived(self, string):
        values = self._packet.receive_data(string)
        self._factory.data_received(values)

    def send_data(self, values):
        string_to_send = self._packet.prepare_to_send(values)
        self.sendString(string_to_send)


class SimpleServerFactory(protocol.Factory):

    def __init__(
            self,
            client_connection_made_callback,
            client_connection_lost_callback,
            data_received_callback
    ):
        self.clients = []
        self.client_connection_made_callback = client_connection_made_callback
        self.client_connection_lost_callback = client_connection_lost_callback
        self.data_received_callback = data_received_callback

    def buildProtocol(self, addr):
        p = SimpleServer(self)
        return p

    def client_connection_made(self, client):
        self.clients.append(client)
        self.client_connection_made_callback()

    def client_connection_lost(self, client):
        self.clients.remove(client)
        self.client_connection_lost_callback()

    def data_received(self, data):
        self.data_received_callback(data)

    def send_data(self, data):
        for client in self.clients:
            client.send_data(data)


class CircleWidget(QWidget):
    def __init__(self, parent=None):
        super(CircleWidget, self).__init__(parent)
        self.nframe = 0
        self.setBackgroundRole(QPalette.Base)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def minimumSizeHint(self):
        return QSize(50, 50)

    def sizeHint(self):
        return QSize(180, 180)

    def next(self):
        self.nframe += 1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.translate(self.width() / 2, self.height() / 2)

        for diameter in range(0, 64, 9):
            delta = abs((self.nframe % 64) - diameter / 2)
            alpha = 255 - (delta * delta) / 4 - diameter
            if alpha > 0:
                painter.setPen(QPen(QColor(0, diameter / 2, 127, alpha), 3))
                painter.drawEllipse(QRectF(
                    -diameter / 2.0,
                    -diameter / 2.0,
                    diameter,
                    diameter))


class LogWidget(QTextBrowser):
    def __init__(self, parent=None):
        super(LogWidget, self).__init__(parent)
        palette = QPalette()
        palette.setColor(QPalette.Base, QColor("#ddddfd"))
        self.setPalette(palette)

dependency_table = {'picam01': [0.0, 0.5, 0.5, 0.5],
                    'picam02': [0.5, 0.0, 0.5, 0.5],
                    'picam03': [0.5, 0.5, 0.0, 0.5],
                    'picam04': [0.5, 0.5, 0.5, 0.0]
                    }

class SampleGUIServerWindow(QMainWindow):
    def __init__(self, reactor, parent=None):
        super(SampleGUIServerWindow, self).__init__(parent)
        self.reactor = reactor

        self.create_main_frame()
        self.create_server()
        self.create_timer()
        self.win = self.create_graphs_window()

        # ## global variables ###
        # white pixel percentage
        self._percentage = np.zeros((4, 1))
        # current activation level
        self._activation = np.zeros((4, 1))
        # current neighbouring nodes activation level
        self._activation_neighbours = np.zeros((4, 1))
        # activation level history
        self._activation_history = np.zeros((4, 200))

    def create_graphs_window(self):
        # set default background color to white
        pg.setConfigOption('background', 'w')
        # open the plot window, set properties
        win = pg.GraphicsWindow(title="VSN activity monitor")
        win.resize(1400, 800)
        win.setWindowTitle('VSN activity monitor')

        #setup plot 1
        cam_plot_1 = win.addPlot(title="picam01")
        self._curve_1 = cam_plot_1.plot(pen='r')
        self._bar_1 = pg.PlotCurveItem([0, 200], [0], stepMode=True, fillLevel=0, brush=(0, 0, 255, 20))
        cam_plot_1.addItem(self._bar_1)
        #set the scale of the plot
        cam_plot_1.setYRange(0, 100)

        #setup plot 2
        cam_plot_2 = win.addPlot(title="picam02")
        self._curve_2 = cam_plot_2.plot(pen='r')
        self._bar_2 = pg.PlotCurveItem([0, 200], [0], stepMode=True, fillLevel=0, brush=(0, 0, 255, 20))
        cam_plot_2.addItem(self._bar_2)
        #set the scale of the plot
        cam_plot_2.setYRange(0, 100)

        #next row
        win.nextRow()

        #setup plot 3
        cam_plot_3 = win.addPlot(title="picam03")
        self._curve_3 = cam_plot_3.plot(pen='r')
        self._bar_3 = pg.PlotCurveItem([0, 200], [0], stepMode=True, fillLevel=0, brush=(0, 0, 255, 20))
        cam_plot_3.addItem(self._bar_3)
        #set the scale of the plot
        cam_plot_3.setYRange(0, 100)

        #setup plot 3
        cam_plot_4 = win.addPlot(title="picam04")
        self._curve_4 = cam_plot_4.plot(pen='r')
        self._bar_4 = pg.PlotCurveItem([0, 200], [0], stepMode=True, fillLevel=0, brush=(0, 0, 255, 20))
        cam_plot_4.addItem(self._bar_4)
        #set the scale of the plot
        cam_plot_4.setYRange(0, 100)

        timer_plot_1 = QtCore.QTimer(self)
        timer_plot_1.timeout.connect(self.update_plot_1)
        timer_plot_1.start(200)

        return win

    def update_plot_1(self):

        self._curve_1.setData(self._activation_history[0])
        self._bar_1.setData([0, 20], self._percentage[0])

        self._curve_2.setData(self._activation_history[1])
        self._bar_2.setData([0, 20], self._percentage[1])

        self._curve_3.setData(self._activation_history[2])
        self._bar_3.setData([0, 20], self._percentage[2])

        self._curve_4.setData(self._activation_history[3])
        self._bar_4.setData([0, 20], self._percentage[3])

        for idx in range(0, 4):
            self._activation_history[idx] = np.roll(self._activation_history[idx], -1)
            self._activation_history[idx][199] = self._activation[idx]
            #self._activation_history[idx][199] = random.randint(1, 100)

    def create_main_frame(self):
        self.circle_widget = CircleWidget()
        self.doit_button = QPushButton('Do it!')
        self.doit_button.clicked.connect(self.on_doit)
        self.log_widget = LogWidget()

        hbox = QHBoxLayout()
        hbox.addWidget(self.circle_widget)
        hbox.addWidget(self.doit_button)
        hbox.addWidget(self.log_widget)

        main_frame = QWidget()
        main_frame.setLayout(hbox)

        self.setCentralWidget(main_frame)

    def create_timer(self):
        self.circle_timer = QTimer(self)
        self.circle_timer.timeout.connect(self.circle_widget.next)
        self.circle_timer.start(25)

    def create_server(self):
        self.server = SimpleServerFactory(
                        self.on_client_connection_made,
                        self.on_client_connection_lost,
                        self.on_client_receive)

    def on_doit(self):
        self.log('Connecting...')
        # When the connection is made, self.client calls the on_client_connect
        # callback.
        #
        endpoint = TCP4ServerEndpoint(reactor, TCP_PORT)
        endpoint.listen(self.server)

    def on_client_connection_made(self):
        self.log('Connected to server. Sending...')
        #self.server.send_data([0, 10, 45, 99])

    def on_client_connection_lost(self):
        # reason is a twisted.python.failure.Failure  object
        self.log('Connection failed')

    def on_client_receive(self, msg):
        #self.log('Client reply: %s' % msg)
        self.log('Received data')

        camera_number, white_pixels, activation_level = msg

        self._activation[0] = activation_level
        #
        # for i, data_item in enumerate(msg):
        #     self._activation[i] = data_item

    def log(self, msg):
        timestamp = '[%010.3f]' % time.clock()
        self.log_widget.append(timestamp + ' ' + str(msg))

    def closeEvent(self, e):
        self.reactor.stop()


#-------------------------------------------------------------------------------

TCP_PORT = 50001

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # try:
    #     import qt4reactor
    # except ImportError:
    #     # Maybe qt4reactor is placed inside twisted.internet in site-packages?
    #     from twisted.internet import qt4reactor
    qt4reactor.install()

    from twisted.internet import reactor
    main_window = SampleGUIServerWindow(reactor)
    main_window.show()

    reactor.run()
