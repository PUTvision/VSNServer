import socket
import cv2
import numpy as np
import threading
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import time

# import pyqtgraph.examples
# pyqtgraph.examples.run()

### global variables ###
#white pixel percentage
percentage = np.zeros((4, 1))
#activation level history
activation_history = np.zeros((4, 200))
decimg = []

### connection details ###
TCP_IP = '192.168.0.100'
TCP_PORT = 5001

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
    serversocket.bind((TCP_IP, TCP_PORT))
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
    global percentage, activation_history, decimg
    while True:
        node = recvall(clientsocket, 32)
        percentage[0] = float(recvall(clientsocket, 32))
        activation_level = float(recvall(clientsocket, 32)) + 1
        #receive the length of the image payload then pull the whole image through the socket
        length = recvall(clientsocket, 32)
        string_data = recvall(clientsocket, int(length))
        data = np.fromstring(string_data, dtype='uint8')
        #decode jpg image to numpy array and display
        decimg = cv2.imdecode(data, 1)
        if(decimg != None):
            cv2.imshow('SERVER', decimg)
        activation_history[0] = np.roll(activation_history[0], -1)
        activation_history[0][199] = activation_level
        key = cv2.waitKey(1)

def update_plot_1():
    global curve_1, bar_1, cam_plot_1
    curve_1.setData(activation_history[0])
    bar_1.setData([0, 200], percentage[0])

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
cam_plot_1.setYRange(0, 300)

#setup plot 2
cam_plot_2 = win.addPlot(title="picam02")
curve_2 = cam_plot_2.plot(pen='r')
bar_2 = pg.PlotCurveItem([0, 200], [0], stepMode=True, fillLevel=0, brush=(0, 0, 255, 20))
cam_plot_2.addItem(bar_2)
#set the scale of the plot
cam_plot_2.setYRange(0, 300)

#next row
win.nextRow()

#setup plot 3
cam_plot_3 = win.addPlot(title="picam03")
curve_3 = cam_plot_3.plot(pen='r')
bar_3 = pg.PlotCurveItem([0, 200], [0], stepMode=True, fillLevel=0, brush=(0, 0, 255, 20))
cam_plot_3.addItem(bar_3)
#set the scale of the plot
cam_plot_3.setYRange(0, 300)

#setup plot 3
cam_plot_4 = win.addPlot(title="picam04")
curve_4 = cam_plot_4.plot(pen='r')
bar_4 = pg.PlotCurveItem([0, 200], [0], stepMode=True, fillLevel=0, brush=(0, 0, 255, 20))
cam_plot_4.addItem(bar_4)
#set the scale of the plot
cam_plot_4.setYRange(0, 300)


timer_plot_1 = QtCore.QTimer()
timer_plot_1.timeout.connect(update_plot_1)
timer_plot_1.start(50)

if __name__ == '__main__':
    server_thread = threading.Thread(target=incoming, args=())
    server_thread.daemon = True
    server_thread.start()
    #thread.start_new_thread(incoming)
    QtGui.QApplication.instance().exec_()
