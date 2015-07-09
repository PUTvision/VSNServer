__author__ = 'Amin'

import sys
import time
import asyncio
import numpy as np
import cv2

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from quamash import QEventLoop
from pyqtgraph.Qt import QtGui, QtCore

from server.VSNServer import VSNServer
from common import VSNPacket
from common.VSNUtility import Config, ImageType
from server.VSNGraph import VSNGraphController
from server.VSNCamerasData import VSNCameras

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class LogWidget(QTextBrowser):
    def __init__(self, parent=None):
        super(LogWidget, self).__init__(parent)
        palette = QPalette()
        palette.setColor(QPalette.Base, QColor('#ddddfd'))
        self.setPalette(palette)


# TODO:
# gather data about state of each camera - how long it was in low-power and how long in high power
# ability to change gain and sample time on the fly
# ability to choose (from GUI) if image should be send or not)


class SampleGUIServerWindow(QMainWindow):
    def __init__(self, event_loop: asyncio.BaseEventLoop, parent=None):
        self.server = None

        super(SampleGUIServerWindow, self).__init__(parent)

        self._graphsController = None

        self.create_main_frame()
        self.create_server()
        self.create_graphs()

        self._cameras = VSNCameras()

        self.__event_loop = event_loop

    def create_server(self):
        self.server = VSNServer(
            Config.server['listening_address'],
            Config.server['listening_port'],
            self.on_client_connection_made,
            self.on_client_connection_lost,
            VSNPacket.ServerPacketRouter(self.on_client_data_received, self.on_client_configuration_received)
        )
        self.log('Connecting...')

    def create_main_frame(self):
        # first row
        hbox_row_1 = QHBoxLayout()

        self.log_widget = LogWidget()
        self.label_image = QLabel()
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

        self.clear_history_button = QPushButton('Clear history')
        self.clear_history_button.clicked.connect(self.on_clear_history)

        hbox_row_2.addWidget(self.combo_box_cameras)
        hbox_row_2.addWidget(self.button_choose_camera)
        hbox_row_2.addWidget(self.doit_button)
        hbox_row_2.addWidget(self.clear_history_button)

        # TODO: add combo box and QLineEdit to set all the parameters

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox_row_1)
        vbox.addLayout(hbox_row_2)

        vbox.addLayout(self._create_status_monitor())

        main_frame = QWidget()
        main_frame.setLayout(vbox)

        self.setCentralWidget(main_frame)

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

        label_description = QtGui.QLabel('picam_name\t' +
                                         'active_pixels\t' +
                                         'activity_level\t' +
                                         'neighbours\t' +
                                         'gain\t' +
                                         'sample_time\t' +
                                         'low_power_ticks\t' +
                                         'normal_ticks'
                                         )
        vbox.addWidget(label_description)

        for i in range(1, 6):
            picam_name = 'picam' + str(i).zfill(2)
            self._picam_labels[picam_name] = QtGui.QLabel()
            self._picam_labels[picam_name].setText(picam_name + ': ')

            vbox.addWidget(self._picam_labels[picam_name])

        return vbox

    def _update_status_monitor(self, camera_number):
        camera_name, \
        active_pixels, \
        activation_level, \
        neighbours, \
        gain, \
        sample_time, \
        low_power_ticks, \
        normal_ticks = self._cameras.get_status(camera_number)

        status = camera_name + '\t\t' + \
                 '{:.2f}'.format(active_pixels) + '\t\t' + \
                 '{:.2f}'.format(activation_level) + '\t\t' + \
                 '{:.2f}'.format(neighbours) + '\t\t' + \
                 '{0: <3}'.format(gain) + '\t' + \
                 '{:.2f}'.format(sample_time) + '\t\t' + \
                 '{0: <4}'.format(low_power_ticks) + '\t\t' + \
                 '{0: <4}'.format(normal_ticks)

        self._picam_labels[camera_name].setText(status)

    def on_choose_camera_clicked(self):
        self._cameras.choose_camera_to_stream(self.combo_box_cameras.currentText())

    def on_doit(self):
        # tests
        # packet_to_client = VSNPacketToClient()
        # packet_to_client.set(4.5, ImageType.background, False)
        # self.server.send_packet_to_all_clients(packet_to_client)

        # test for adding new row to the graph window
        # self._graphsController.add_new_graph()

        self._cameras.save_cameras_data_to_files()

    def on_clear_history(self):
        self._cameras.clear_cameras_data()

    def on_client_connection_made(self, client):
        self.log('Client connected')

        if Config.clients['hostname_based_ids']:
            client.send(VSNPacket.ConfigurationPacketToClient())
        else:
            client.send(VSNPacket.ConfigurationPacketToClient(client.id))

    def on_client_connection_lost(self):
        self.log('Client disconnected')

    def on_client_data_received(self, client, packet: VSNPacket.DataPacketToServer):
        self.log('Received data')

        self.service_client_data(
            packet.white_pixels,
            packet.activation_level,
            client
        )

        if packet.image is not None:
            self.service_client_image(packet.image)

    def on_client_configuration_received(self, client, packet: VSNPacket.DataPacketToServer):
        self.log('Received configuration ' + repr(packet))
        client.id = packet.node_id

    def service_client_image(self, image_as_string: str):
        data = np.fromstring(image_as_string, dtype='uint8')
        # decode jpg image to numpy array and display
        decimg = cv2.imdecode(data, cv2.IMREAD_GRAYSCALE)

        qi = QtGui.QImage(decimg, 320, 240, QtGui.QImage.Format_Indexed8)
        self.label_image.setPixmap(QtGui.QPixmap.fromImage(qi))

    def service_client_data(self, white_pixels, activation_level, client):
        activation_neighbours = self._cameras.update_state(client.id, activation_level, white_pixels)

        packet_to_send = VSNPacket.DataPacketToClient(activation_neighbours,
                                                      ImageType.foreground,
                                                      self._cameras.get_flag_send_image(client.id))
        client.send(packet_to_send)

        # TODO: remove node index variable and use camera name instead
        node_index = client.id - 1
        self._graphsController.set_new_values(
            node_index,
            activation_level + activation_neighbours,
            white_pixels
        )

        self._update_status_monitor(client.id)

    def log(self, msg):
        timestamp = '[%010.3f]' % time.clock()
        self.log_widget.append(timestamp + ' ' + str(msg))

    def closeEvent(self, e):
        self.server.stop()
        self.__event_loop.stop()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    main_window = SampleGUIServerWindow(loop)
    main_window.show()

    loop.run_forever()
    loop.close()
