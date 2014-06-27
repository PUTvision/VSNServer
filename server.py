from pydoc import serve
import socket
import cv2
import numpy as np
import threading
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg

### global variables ###
#white pixel percentage
percentage = 0
#activation level history
activation_history = [0] * 200
decimg = []

### connection details ###
TCP_IP = '192.168.0.100'
TCP_PORT = 5001

# receives complete compressed image payload
def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        #TODO: it may be ebough to comment the line below
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
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
        percentage = float(recvall(clientsocket, 16))
        activation_level = float(recvall(clientsocket, 16))
        #receive the length of the image payload then pull the whole image through the socket
        length = recvall(clientsocket, 16)
        # TODO: right now all data is received (according to length), but there's no warranty that all has been sent
        # TODO: recvall returns none in such case
        string_data = recvall(clientsocket, int(length))
        data = np.fromstring(string_data, dtype='uint8')
        #decode jpg image to numpy array and display
        decimg = cv2.imdecode(data, 1)
        if(decimg != None):
            cv2.imshow('SERVER', decimg)
        activation_history.append(activation_level)
        del activation_history[0]
        key = cv2.waitKey(1)

def update_plot_1():
    global curve_1, bar_1, cam_plot_1
    curve_1.setData(activation_history)
    bar_1.setData([0, 200], [percentage])

#table holding a 200-sample history of activation level
activation_history = [0] * 200

# set default background color to white
pg.setConfigOption('background', 'w')
# open the plot window, set properties
win = pg.GraphicsWindow(title="VSN activity monitor")
win.resize(1000, 600)
win.setWindowTitle('VSN activity monitor')

#setup the plot
cam_plot_1 = win.addPlot(title="picam01")
curve_1 = cam_plot_1.plot(pen='r')
bar_1 = pg.PlotCurveItem([0, 200], [percentage], stepMode=True, fillLevel=0, brush=(0, 0, 255, 20))
cam_plot_1.addItem(bar_1)

timer_plot_1 = QtCore.QTimer()
timer_plot_1.timeout.connect(update_plot_1)
timer_plot_1.start(50)

if __name__ == '__main__':
    server_thread = threading.Thread(target=incoming, args=())
    server_thread.daemon = True
    server_thread.start()
    #thread.start_new_thread(incoming)
    QtGui.QApplication.instance().exec_()
    print "Do I even get here?"
    print decimg

