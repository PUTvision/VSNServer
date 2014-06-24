import socket
import cv2
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec
import time
import math

def lowpass(prev_sample, input):
    gain = 1
    time_constant = 1
    sample_time = 0.1
    output = (gain/time_constant) * input + prev_sample * pow(math.e, -1.0 *(sample_time/time_constant))
    return output


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

activation_level_past = 0
activation_history = [0] * 200

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(True)

conn, addr = s.accept()
fig = plt.figure()

gs = gridspec.GridSpec(1, 2, width_ratios=[2,5])

ax1 = plt.subplot(gs[0])
ax2 = plt.subplot(gs[1])


plt.ion()
plt.show()
plt.sca(ax1)

plt.ylim([0, 100])
plt.xlim([0, 3])
rects = ax1.bar([1], 0, 1)


plt.sca(ax2)
plt.ylim([0, 200])
line, = ax2.plot(activation_history)


while True:
    nonzero = float(recvall(conn, 16))
    length = recvall(conn, 16)
    stringData = recvall(conn, int(length))
    data = np.fromstring(stringData, dtype='uint8')
    decimg = cv2.imdecode(data, 1)
    cv2.imshow('SERVER', decimg)

    height, width = decimg.shape[:2]
    percentage = (nonzero * 100 / (height * width))
    print "white pixel percentage %.3f" % percentage, " %", "\r",

    activation_level = lowpass(activation_level_past, percentage)
    activation_level_past = activation_level

    values = [percentage]

    for rect, h in zip(rects, values):
        rect.set_height(h)

    activation_history.append(activation_level)
    del activation_history[0]
    line.set_ydata(activation_history)

    plt.draw()

    key = cv2.waitKey(1)
    if key == 27:
        break

s.close()

cv2.waitKey(0)
cv2.destroyAllWindows()