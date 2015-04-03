__author__ = 'Amin'

from twisted.internet.endpoints import TCP4ServerEndpoint
#from twisted.internet import reactor

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys
import time

import qt4reactor

from pyqtgraph.Qt import QtGui, QtCore

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

import pyqtgraph as pg

import numpy as np

import random

from VSNServer import VSNServerFactory
from VSNPacket import VSNPacketToClient
from VSNPacket import IMAGE_TYPES


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


class CameraGraph:
    def __init__(self, camera_number):
        self.plot_title = "picam" + str(camera_number)

        self.white_pixels_percentage = np.zeros(1)
        self.neighbouring_node_activation_level = 0.0
        self.activation_level_history = np.zeros(200)

        # graph elements
        self._curve = None
        self._bar = None

    def add_graph(self, window):
        #setup plot
        cam_plot = window.addPlot(title=self.plot_title)
        self._curve = cam_plot.plot(pen='r')
        self._bar = pg.PlotCurveItem([0, 200], [0], stepMode=True, fillLevel=0, brush=(0, 0, 255, 20))
        cam_plot.addItem(self._bar)
        #set the scale of the plot
        cam_plot.setYRange(0, 100)

    def update_graph(self, activation_level):
        self._bar.setData([0, 20], self.white_pixels_percentage)
        self._curve.setData(self.activation_level_history)

        self.activation_level_history = np.roll(self.activation_level_history, -1)
        self.activation_level_history[199] = activation_level


class SampleGUIServerWindow(QMainWindow):
    def __init__(self, reactor, parent=None):
        super(SampleGUIServerWindow, self).__init__(parent)
        self.reactor = reactor

        self.create_main_frame()
        self.create_server()
        self.create_timer()

        # ## global variables ###
        # white pixel percentage
        self._percentage = np.zeros((4, 1))
        # current activation level
        self._activation = np.zeros((4, 1))
        # current neighbouring nodes activation level
        self._activation_neighbours = np.zeros((4, 1))

        self._graphs = [CameraGraph(i) for i in xrange(4)]

        self.win = self.create_graphs_window()

    def create_graphs_window(self):
        # set default background color to white
        pg.setConfigOption('background', 'w')
        # open the plot window, set properties
        win = pg.GraphicsWindow(title="VSN activity monitor")
        win.resize(1400, 800)
        win.setWindowTitle('VSN activity monitor')

        for i, graph in enumerate(self._graphs):
            if i > 0 and i % 2 == 0:
                win.nextRow()
            graph.add_graph(win)

        timer_plot = QtCore.QTimer(self)
        timer_plot.timeout.connect(self.update_plot)
        timer_plot.start(200)

        return win

    def update_plot(self):
        for i, graph in enumerate(self._graphs):
            if i < 4:
                graph.white_pixels_percentage = self._percentage[i]
                graph.update_graph(self._activation[i])


    def create_main_frame(self):
        self.circle_widget = CircleWidget()
        self.doit_button = QPushButton('Do it!')
        self.doit_button.clicked.connect(self.on_doit)
        self.log_widget = LogWidget()

        self.label = QtGui.QLabel()

        myPixmap = QtGui.QPixmap(_fromUtf8('Crazy-Cat.jpg'))
        myScaledPixmap = myPixmap.scaled(self.label.size(), Qt.KeepAspectRatio)
        self.label.setPixmap(myScaledPixmap)

        hbox = QHBoxLayout()
        hbox.addWidget(self.circle_widget)
        hbox.addWidget(self.doit_button)
        hbox.addWidget(self.log_widget)
        hbox.addWidget(self.label)

        main_frame = QWidget()
        main_frame.setLayout(hbox)



        self.setCentralWidget(main_frame)

    def create_timer(self):
        self.circle_timer = QTimer(self)
        self.circle_timer.timeout.connect(self.circle_widget.next)
        self.circle_timer.start(25)

    def create_server(self):
        self.server = VSNServerFactory(
                        self.on_client_connection_made,
                        self.on_client_connection_lost,
                        self.on_client_data_received)
        self.log('Connecting...')
        # When the connection is made, self.client calls the on_client_connect
        # callback.
        #
        endpoint = TCP4ServerEndpoint(reactor, TCP_PORT)
        endpoint.listen(self.server)


    def on_doit(self):
        packet_to_client = VSNPacketToClient()
        packet_to_client.set(4.5, IMAGE_TYPES.background, False)
        self.server.send_packet_to_all_clients(packet_to_client)

        # test for adding new row to the graph window
        new_camera_graph = CameraGraph(5)
        if len(self._graphs) % 2 == 0:
            self.win.nextRow()
        new_camera_graph.add_graph(self.win)
        self._graphs.append(new_camera_graph)

    def on_client_connection_made(self):
        self.log('Connected to server. Sending...')
        #self.server.send_data([0, 10, 45, 99])

    def on_client_connection_lost(self):
        # reason is a twisted.python.failure.Failure  object
        self.log('Connection failed')

    def on_client_data_received(self, packet):
        #self.log('Client reply: %s' % msg)
        self.log('Received data')

        camera_number = packet.camera_number
        white_pixels = packet.white_pixels
        activation_level = packet.activation_level

        self.service_client(camera_number, white_pixels, activation_level)

    def service_client(self, camera_number, white_pixels, activation_level):
        node_index = camera_number
        node_name = "picam" + str(node_index).zfill(2)

        self._activation_neighbours[node_index] = 0
        for idx in xrange(0, 3):
            self._activation_neighbours[node_index] += dependency_table[node_name][idx] * self._activation[idx][0]
        # still TODO (the line below)
        #clientsocket.send(str(activation_neighbours[node_index][0]).ljust(32))
        self._activation[node_index] = activation_level + self._activation_neighbours[0][0]
        self._percentage[node_index] = white_pixels

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
