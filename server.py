import socket
import cv2
import numpy as np
import threading
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import time

# TODO: create a dependency table as python dictionary with list, e.g. table = {'picam01' : [1.5, 0.2, 1.1, 0, 0]}
# elements can then be accessed as table['picam0'][1] -> 1st element of list corresponding to the 'picam01' entry

# import pyqtgraph.examples
# pyqtgraph.examples.run()

dependency_table = {'picam01': [0.0, 0.5, 0.5, 0.5],
                    'picam02': [0.5, 0.0, 0.5, 0.5],
                    'picam03': [0.5, 0.5, 0.0, 0.5],
                    'picam04': [0.5, 0.5, 0.5, 0.0]
                    }


# ## global variables ###
# white pixel percentage
percentage = np.zeros((4, 1))
# current activation level
activation = np.zeros((4, 1))
# current neighbouring nodes activation level
activation_neighbours = np.zeros((4, 1))
# activation level history
activation_history = np.zeros((4, 200))
decimg = []

### connection details ###
TCP_PORT = 50001


# receives complete compressed image payload
def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if newbuf is not None:
            buf += newbuf
            count -= len(newbuf)
        else:
            time.sleep(0.001)
    return buf


def incoming():
    #create socket and listen for incoming client requests
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(('', TCP_PORT))
    serversocket.listen(True)
    print "Server is listening for connections"
    while True:
        clientsocket, clientaddr = serversocket.accept()
        if clientaddr:
            print "Accepted connection from: ", clientaddr
            client_thread = threading.Thread(target=service_clients, args=(clientsocket, clientaddr))
            client_thread.daemon = True
            client_thread.start()
            key = cv2.waitKey(1)


def service_clients(clientsocket, clientaddr):
    global percentage, decimg, activation
    while True:
        node_name = recvall(clientsocket, 8)
        whitepixels = float(recvall(clientsocket, 32))
        activation_level = float(recvall(clientsocket, 32)) + 1
        #receive the length of the image payload then pull the whole image through the socket
        length = recvall(clientsocket, 32)
        string_data = recvall(clientsocket, int(length))
        data = np.fromstring(string_data, dtype='uint8')
        #decode jpg image to numpy array and display
        decimg = cv2.imdecode(data, 1)
        node_index = 0
        if node_name == "picam01 ":
            node_index = 0
        elif node_name == "picam02 ":
            node_index = 1
        elif node_name == "picam03 ":
            node_index = 2
        elif node_name == "picam04 ":
            node_index = 3

        activation_neighbours[node_index] = 0
        for idx in xrange(0, 3):
            activation_neighbours[node_index] += dependency_table[node_name][idx] * activation[idx][0]
        clientsocket.send(str(activation_neighbours[node_index][0]).ljust(32))
        activation[node_index] = activation_level + activation_neighbours[0][0]
        percentage[node_index] = whitepixels

        key = cv2.waitKey(1)
        print(np.transpose(activation_neighbours))


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

if __name__ == '__main__':
    server_thread = threading.Thread(target=incoming, args=())
    server_thread.daemon = True
    server_thread.start()
    #thread.start_new_thread(incoming)
    QtGui.QApplication.instance().exec_()
