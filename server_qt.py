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

from VSNActivityController import GainSampletimeTuple


class VSNCameraData:
    def __init__(self):
        self._activation_level = 0.0
        self.percentage_of_active_pixels = 0.0
        # current neighbouring nodes activation level
        self.activation_neighbours = 0.0                           # weighted activity of neighbouring nodes
        self.flag_send_image = False

        self.ticks_in_low_power_mode = 0
        self.ticks_in_normal_operation_mode = 0

        # TODO: make below parameters meaningful
        self._parameters_below_threshold = GainSampletimeTuple(2.0, 1.0)
        self._parameters_above_threshold = GainSampletimeTuple(0.1, 0.1)
        self._activation_level_threshold = 10.0
        self._parameters = self._parameters_below_threshold         # sample time and gain at startup
        self.image_type = IMAGE_TYPES.foreground

    def update_activation_level(self, activation_level):
        if activation_level < self._activation_level_threshold:
            self.ticks_in_low_power_mode += 10
        else:
            self.ticks_in_normal_operation_mode += 1

        self._activation_level = activation_level


class VSNCameras:
    def __init__(self):
        # TODO: this should be automaticly created or even put inside the CameraData class
        self._dependency_table = {
            'picam01': [0.0, 0.5, 0.5, 0.5],
            'picam02': [0.5, 0.0, 0.5, 0.5],
            'picam03': [0.5, 0.5, 0.0, 0.5],
            'picam04': [0.5, 0.5, 0.5, 0.0]
        }

        self.cameras = {}
        # TODO: remove the automatic creation of 4 cameras and to is as new cameras connect
        self.add_camera(1)
        self.add_camera(2)
        self.add_camera(3)
        self.add_camera(4)

    def choose_camera_to_stream(self, camera_name):
        for key in self.cameras:
            self.cameras[key].flag_send_image = False
        self.cameras[str(camera_name)].flag_send_image = True

    def get_flag_send_image(self, camera_number):
        camera_name = self._convert_camera_number_to_camera_name(camera_number)
        return self.cameras[camera_name].flag_send_image

    def get_activation_neighbours(self, camera_number):
        camera_name = self._convert_camera_number_to_camera_name(camera_number)
        return self.cameras[camera_name].activation_neighbours

    def get_percentage_of_active_pixels(self, camera_number):
        camera_name = self._convert_camera_number_to_camera_name(camera_number)
        return self.cameras[camera_name].percentage_of_active_pixels

    def add_camera(self, camera_number):
        camera_name = self._convert_camera_number_to_camera_name(camera_number)
        self.cameras[camera_name] = VSNCameraData()

    def _convert_camera_number_to_camera_name(self, camera_number):
        camera_name = "picam" + str(camera_number).zfill(2)
        return camera_name

    def update_state(self, camera_number, activation_level, percentage_of_active_pixels):
        camera_name = self._convert_camera_number_to_camera_name(camera_number)

        self.cameras[camera_name].update_activation_level(activation_level)

        # update number of active pixels
        self.cameras[camera_name].percentage_of_active_pixels = percentage_of_active_pixels

        return self._calculate_neighbour_activation_level(camera_name)

    def _calculate_neighbour_activation_level(self, camera_name):
        # TODO: change it to check against the real number of cameras in the system
        self.cameras[camera_name].activation_neighbours = 0.0
        for idx in xrange(0, 3):
            # idx+1 is used because cameras are numbered 1, 2, 3, 4
            current_camera_name = "picam" + str(idx+1).zfill(2)
            self.cameras[camera_name].activation_neighbours += \
                self._dependency_table[camera_name][idx] * self.cameras[current_camera_name].percentage_of_active_pixels

        return self.cameras[camera_name].activation_neighbours

        #self._activation_neighbours[node_index] = 0
        #for idx in xrange(0, 3):
        #    self._activation_neighbours[node_index] += \
        #        dependency_table[node_name][idx] * self._graphsController._percentages[idx]

# TODO:
# gather data about state of each camera - how long it was in low-power and how long in high power
# ability to change gain and sample time on the fly
# ability to choose (from GUI) if image should be send or not)


class SampleGUIServerWindow(QMainWindow):
    def __init__(self, reactor, parent=None):
        super(SampleGUIServerWindow, self).__init__(parent)
        self.reactor = reactor

        self.create_main_frame()
        self.create_server()
        self.create_timer()

        self._graphsController = VSNGraphController()
        self._graphsController.create_graph_window()
        self._graphsController.add_new_graph()
        self._graphsController.add_new_graph()
        self._graphsController.add_new_graph()
        self._graphsController.add_new_graph()

        timer_plot = QtCore.QTimer(self)
        timer_plot.timeout.connect(self._graphsController.update_graphs)
        timer_plot.start(200)

        self._cameras = VSNCameras()

    def create_main_frame(self):
        self.circle_widget = CircleWidget()
        self.doit_button = QPushButton('Do it!')
        self.doit_button.clicked.connect(self.on_doit)
        self.log_widget = LogWidget()

        self.label_image = QtGui.QLabel()
        myPixmap = QtGui.QPixmap(_fromUtf8('Crazy-Cat.jpg'))
        myScaledPixmap = myPixmap.scaled(self.label_image.size(), Qt.KeepAspectRatio)
        self.label_image.setPixmap(myScaledPixmap)

        self._label_picam1 = QtGui.QLabel("picam01")
        self._label_picam2 = QtGui.QLabel("picam02")
        self._label_picam3 = QtGui.QLabel("picam03")
        self._label_picam4 = QtGui.QLabel("picam04")
        self._label_activations_neighbours = QtGui.QLabel("activations_neighbours")

        hbox_row_1 = QHBoxLayout()
        hbox_row_1.addWidget(self.log_widget)
        hbox_row_1.addWidget(self.label_image)

        hbox_row_2 = QHBoxLayout()
        #hbox_row_2.addWidget(self.circle_widget)
        hbox_row_2.addWidget(self._label_picam1)
        hbox_row_2.addWidget(self._label_picam2)
        hbox_row_2.addWidget(self._label_picam3)
        hbox_row_2.addWidget(self._label_picam4)
        hbox_row_2.addWidget(self.doit_button)


        hbox_row_3 = QHBoxLayout()
        cameras = ['picam01',
                   'picam02',
                   'picam03',
                   'picam04'
        ]
        # Create and fill the combo box to choose the salutation
        self.combo_box_cameras = QComboBox()
        self.combo_box_cameras.addItems(cameras)
        hbox_row_3.addWidget(self.combo_box_cameras)
        self.button_choose_camera = QPushButton('choose')
        self.button_choose_camera.clicked.connect(self.on_choose_camera_clicked)
        hbox_row_3.addWidget(self.button_choose_camera)
        # TODO: add combo box and QLineEdit to set all the parameters

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox_row_1)
        vbox.addLayout(hbox_row_2)
        vbox.addLayout(hbox_row_3)
        vbox.addWidget(self._label_activations_neighbours)

        main_frame = QWidget()
        main_frame.setLayout(vbox)

        self.setCentralWidget(main_frame)

    def create_timer(self):
        self.circle_timer = QTimer(self)
        self.circle_timer.timeout.connect(self.circle_widget.next)
        self.circle_timer.start(25)

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
        endpoint = TCP4ServerEndpoint(reactor, TCP_PORT)
        endpoint.listen(self.server)

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
        # old way
        # TODO - this should be corrected
        #node_index = camera_number-1
        #node_name = "picam" + str(camera_number).zfill(2)

        #self._activation_neighbours[node_index] = 0
        #for idx in xrange(0, 3):
        #    self._activation_neighbours[node_index] += \
        #        dependency_table[node_name][idx] * self._graphsController._percentages[idx]
                #dependency_table[node_name][idx] * self._graphsController._activations[idx]

        activation_neighbours = self._cameras.update_state(camera_number, activation_level, white_pixels)

        packet_to_send = VSNPacketToClient()
        packet_to_send.set(
            #self._activation_neighbours[node_index],
            activation_neighbours,
            IMAGE_TYPES.foreground,
            self._cameras.get_flag_send_image(camera_number)
        )
        client.send_packet(packet_to_send)

        # TODO: remove node index variable and use camera name instead
        node_index = camera_number - 1
        self._graphsController.set_new_values(
            node_index,
            #activation_level + self._activation_neighbours[node_index],
            activation_level + activation_neighbours,
            white_pixels
        )

        info = "Camera: " + str(camera_number) + ", " \
               "{:.2f}".format(activation_level) + ", " + \
               "{:.2f}".format(white_pixels) + ", " + \
               ""
        if node_index == 0:
            self._label_picam1.setText(info)
        elif node_index == 1:
            self._label_picam2.setText(info)
        elif node_index == 2:
            self._label_picam3.setText(info)
        elif node_index == 3:
            self._label_picam4.setText(info)

        #activations_neighbours_text = str(self._activation_neighbours)
        activations_neighbours_text = ""
        activations_neighbours_text += str(self._cameras.get_activation_neighbours(1)) + "\r\n"
        activations_neighbours_text += str(self._cameras.get_activation_neighbours(2)) + "\r\n"
        activations_neighbours_text += str(self._cameras.get_activation_neighbours(3)) + "\r\n"
        activations_neighbours_text += str(self._cameras.get_activation_neighbours(4)) + "\r\n"
        self._label_activations_neighbours.setText(activations_neighbours_text)

    def log(self, msg):
        timestamp = '[%010.3f]' % time.clock()
        self.log_widget.append(timestamp + ' ' + str(msg))

    def closeEvent(self, e):
        self.reactor.stop()


#-------------------------------------------------------------------------------

TCP_PORT = 50001

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
