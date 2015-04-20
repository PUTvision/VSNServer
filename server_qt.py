__author__ = 'Amin'

from twisted.internet.endpoints import TCP4ServerEndpoint

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys
import time

from pyqtgraph.Qt import QtGui, QtCore

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

import numpy as np

import cv2

from VSNServer import VSNServerFactory
from VSNPacket import VSNPacketToClient
from VSNPacket import IMAGE_TYPES
from VSNGraph import VSNGraphController
from VSNCamerasData import VSNCameras


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


# TODO:
# gather data about state of each camera - how long it was in low-power and how long in high power
# ability to change gain and sample time on the fly
# ability to choose (from GUI) if image should be send or not)


class SampleGUIServerWindow(QMainWindow):
    def __init__(self, reactor, parent=None):
        self._TCP_PORT = 50001

        super(SampleGUIServerWindow, self).__init__(parent)
        self.reactor = reactor

        self._graphsController = None

        self.create_main_frame()
        self.create_server()
        self.create_timer()
        self.create_graphs()

        self._cameras = VSNCameras()

    def create_server(self):
        self.server = VSNServerFactory(
                        self.on_client_connection_made,
                        self.on_client_connection_lost,
                        self.on_client_data_received,
                        self.on_client_image_received
        )
        self.log('Connecting...')
        # When the connection is made, self.client calls the on_client_connect
        # callback.
        #
        endpoint = TCP4ServerEndpoint(reactor, self._TCP_PORT)
        endpoint.listen(self.server)

    def create_main_frame(self):
        # unused elements
        self.circle_widget = CircleWidget()
        #hbox_row_2.addWidget(self.circle_widget)

        # first row
        hbox_row_1 = QHBoxLayout()

        self.log_widget = LogWidget()
        self.label_image = QtGui.QLabel()
        myPixmap = QtGui.QPixmap(_fromUtf8('Crazy-Cat.jpg'))
        myScaledPixmap = myPixmap.scaled(self.label_image.size(), Qt.KeepAspectRatio)
        self.label_image.setPixmap(myScaledPixmap)

        hbox_row_1.addWidget(self.log_widget)
        hbox_row_1.addWidget(self.label_image)

        # second row
        hbox_row_2 = QHBoxLayout()

        cameras = ['picam01',
                   'picam02',
                   'picam03',
                   'picam04',
                   'picam05'
        ]
        self.combo_box_cameras = QComboBox()
        self.combo_box_cameras.addItems(cameras)

        self.button_choose_camera = QPushButton('choose')
        self.button_choose_camera.clicked.connect(self.on_choose_camera_clicked)

        self.doit_button = QPushButton('Do it!')
        self.doit_button.clicked.connect(self.on_doit)

        hbox_row_2.addWidget(self.combo_box_cameras)
        hbox_row_2.addWidget(self.button_choose_camera)
        hbox_row_2.addWidget(self.doit_button)

        # TODO: add combo box and QLineEdit to set all the parameters

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox_row_1)
        vbox.addLayout(hbox_row_2)

        vbox.addLayout(self._create_status_monitor())

        main_frame = QWidget()
        main_frame.setLayout(vbox)

        self.setCentralWidget(main_frame)

    def create_timer(self):
        self.circle_timer = QTimer(self)
        self.circle_timer.timeout.connect(self.circle_widget.next)
        self.circle_timer.start(25)

    def create_graphs(self):
        self._graphsController = VSNGraphController()
        self._graphsController.create_graph_window()
        self._graphsController.add_new_graph()
        self._graphsController.add_new_graph()
        self._graphsController.add_new_graph()
        self._graphsController.add_new_graph()
        self._graphsController.add_new_graph()

        timer_plot = QtCore.QTimer(self)
        timer_plot.timeout.connect(self._graphsController.update_graphs)
        timer_plot.start(200)

    def _create_status_monitor(self):
        vbox = QtGui.QVBoxLayout()

        self._picam_labels = {}

        label_description = QtGui.QLabel("picam_name\t" +
                                         "active_pixels\t" +
                                         "activity_level\t" +
                                         "neighbours\t" +
                                         "gain\t" +
                                         "sample_time\t" +
                                         "low_power_ticks\t" +
                                         "normal_ticks"
                                         )
        vbox.addWidget(label_description)

        for i in xrange(1, 6):
            picam_name = "picam" + str(i).zfill(2)
            self._picam_labels[picam_name] = QtGui.QLabel()
            self._picam_labels[picam_name].setText(picam_name + ": ")

            vbox.addWidget(self._picam_labels[picam_name])

        return vbox

    def _update_status_monitor(self, camera_number):
        camera_name, \
        active_pixels, \
        activation_level,\
        neighbours, \
        gain, \
        sample_time, \
        low_power_ticks, \
        normal_ticks = self._cameras.get_status(camera_number)

        status = camera_name + "\t\t" + \
                 "{:.2f}".format(active_pixels) + "\t\t" + \
                 "{:.2f}".format(activation_level) + "\t\t" + \
                 "{:.2f}".format(neighbours) + "\t\t" + \
                 "{0: <3}".format(gain) + "\t" + \
                 "{:.2f}".format(sample_time) + "\t\t" + \
                 "{0: <4}".format(low_power_ticks) + "\t\t" + \
                 "{0: <4}".format(normal_ticks)

        self._picam_labels[camera_name].setText(status)

    def on_choose_camera_clicked(self):
        self._cameras.choose_camera_to_stream(self.combo_box_cameras.currentText())

    def on_doit(self):
        packet_to_client = VSNPacketToClient()
        packet_to_client.set(4.5, IMAGE_TYPES.background, False)
        self.server.send_packet_to_all_clients(packet_to_client)

        # test for adding new row to the graph window
        self._graphsController.add_new_graph()

    def on_client_connection_made(self):
        self.log('Connected to server.')

    def on_client_connection_lost(self):
        # reason is a twisted.python.failure.Failure  object
        self.log('Connection failed')

    def on_client_data_received(self, packet, client):
        self.log('Received data')

        self.service_client(
            packet.camera_number,
            packet.white_pixels,
            packet.activation_level,
            client
        )

    def on_client_image_received(self, image_as_string):
        data = np.fromstring(image_as_string, dtype='uint8')
        #decode jpg image to numpy array and display
        decimg = cv2.imdecode(data, cv2.CV_LOAD_IMAGE_GRAYSCALE)

        qi = QtGui.QImage(decimg, 320, 240, QtGui.QImage.Format_Indexed8)
        self.label_image.setPixmap(QtGui.QPixmap.fromImage(qi))

    def service_client(self, camera_number, white_pixels, activation_level, client):
        activation_neighbours = self._cameras.update_state(camera_number, activation_level, white_pixels)

        packet_to_send = VSNPacketToClient()
        packet_to_send.set(
            activation_neighbours,
            IMAGE_TYPES.foreground,
            self._cameras.get_flag_send_image(camera_number)
        )
        client.send_packet(packet_to_send)

        # TODO: remove node index variable and use camera name instead
        node_index = camera_number - 1
        self._graphsController.set_new_values(
            node_index,
            activation_level + activation_neighbours,
            white_pixels
        )

        self._update_status_monitor(camera_number)

    def log(self, msg):
        timestamp = '[%010.3f]' % time.clock()
        self.log_widget.append(timestamp + ' ' + str(msg))

    def closeEvent(self, e):
        self.reactor.stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    try:
        import qt4reactor
    except ImportError:
        # Maybe qt4reactor is placed inside twisted.internet in site-packages?
        from twisted.internet import qt4reactor
    qt4reactor.install()

    from twisted.internet import reactor
    main_window = SampleGUIServerWindow(reactor)
    main_window.show()

    reactor.run()
