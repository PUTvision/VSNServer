import socket
import cv2
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec

# receives complete compressed image payload
def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf


TCP_IP = '192.168.0.100'
TCP_PORT = 5001

#table holding a 200-sample history of activation level
activation_history = [0] * 200
#create socket and listen for incoming client requests
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(True)
conn, addr = s.accept()

#create a figure with given width ratios
fig = plt.figure()
gs = gridspec.GridSpec(1, 2, width_ratios=[2, 5])
#axes for subplots
ax1 = plt.subplot(gs[0])
ax2 = plt.subplot(gs[1])
#interactive mode for matplotlib
plt.ion()
plt.show()
#scale axis and plot the bar, get bar handle
plt.sca(ax1)
plt.ylim([0, 100])
plt.xlim([0, 3])
rects = ax1.bar([1], 0, 1)

#scale axes and plot the activation history
plt.sca(ax2)
plt.ylim([0, 200])
line, = ax2.plot(activation_history)

while True:
    #receive white pixel percentage and current activation level
    percentage = float(recvall(conn, 16))
    activation_level = float(recvall(conn, 16))
    #receive the length of the image payload then pull the whole image through the socket
    length = recvall(conn, 16)
    stringData = recvall(conn, int(length))
    data = np.fromstring(stringData, dtype='uint8')
    #decode jpg image to numpy array and display
    decimg = cv2.imdecode(data, 1)
    cv2.imshow('SERVER', decimg)

    #update the bar graph
    values = [percentage]
    for rect, h in zip(rects, values):
        rect.set_height(h)
    #update the activation level graph
    activation_history.append(activation_level)
    del activation_history[0]
    line.set_ydata(activation_history)
    #draw the figure
    plt.draw()

    key = cv2.waitKey(1)
    if key == 27:
        break

s.close()

cv2.waitKey(0)
cv2.destroyAllWindows()