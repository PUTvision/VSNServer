__author__ = 'Michal Fularz, Marek Kraft'

import socket
import math
import time
import threading
import cv2
import cv2.cv as cv
import numpy as np


class VSNClient:
    def __init__(self):
        # constant definitions
        #self._SERVER_IP = '192.168.0.100'
        self._SERVER_IP = '127.0.0.1'
        self._SERVER_PORT = 50001

        self._SERVER_INFO = (self._SERVER_IP, self._SERVER_PORT)

        # parameters
        self.activation_level = 0            # default starting activation level
        self.sample_time = 0.1               # sample time at startup
        self.gain = 0.1                      # gain at startup
        self.flag_send_data = False          # default behavior - do not send the image data
        self.activation_neighbours = 0       # weighted activity of neighbouring nodes

        # other
        self.sock = socket.socket()
        self.capture = cv2.VideoCapture()
        self.struct = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        self.background = cv2.cv.CreateMat(320, 240, cv.CV_8UC1)

    # lowpass filter function modelled after a 1st order inertial object transformed using delta minus method
    def lowpass(self, prev_sample, input_val, sample_time_lowpass):
        time_constant = 1
        output = (self.gain / time_constant) * input_val + prev_sample * pow(math.e, -1.0 * (sample_time_lowpass / time_constant))
        return output

    # receives the given number of bytes from socket
    def recv_all(self, count):
        # TODO: when evertything is working ok, remove this local variable
        recv_socket = self.sock
        buf = b''
        while count:
            newbuf = recv_socket.recv(count)
            if newbuf is not None:
                buf += newbuf
                count -= len(newbuf)
            else:
                time.sleep(0.05)
        return buf

    def get_params(self):
        while True:
            self.activation_neighbours = float(self.recv_all(32))
            time.sleep(0.05)

    def img_process(self):
        #lock.acquire()

        # TODO: remove threading and change it to periodic call to this method
        #queue a call to itself after sample time has elapsed to ensure periodic firing
        threading.Timer(self.sample_time, self.img_process).start()

        # grab and process frame, update the background and foreground model
        ret, frame = self.capture.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mask_gt = cv2.compare(self.background, gray, cv2.CMP_GT)
        mask_lt = cv2.compare(self.background, gray, cv2.CMP_LT)

        self.background += mask_lt / 128.0
        self.background -= mask_gt / 128.0

        difference = cv2.absdiff(self.background, gray)
        difference = cv2.medianBlur(difference, 3)
        display = cv2.compare(difference, 6, cv2.CMP_GT)
        eroded = cv2.erode(display, self.struct)
        dilated = cv2.dilate(eroded, self.struct)
        nonzero = cv2.countNonZero(dilated)

        height, width = dilated.shape[:2]
        percentage = (nonzero * 100 / (height * width))

        # compute the sensor state based on captured images
        activation_level_new = self.lowpass(self.activation_level, percentage, self.sample_time)
        activation_level = activation_level_new + self.activation_neighbours

        ##### TODO: implement functionality allowing to choose whether or not to send the image of choice (fg, bg, raw)

        # encode image for sending
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        result, img_encoded = cv2.imencode('.jpg', dilated, encode_param)
        data = np.array(img_encoded)

        string_data = data.tostring()

        ###### to do ends here

        # send the obligatory sensor state info
        self.sock.send(socket.gethostname().ljust(8))
        self.sock.send(str(percentage).ljust(32))
        self.sock.send(str(activation_level).ljust(32))
        self.sock.send(str(len(string_data)).ljust(32))
        self.sock.send(string_data)

        #lock.release()

        # simple profiling, uncomment if necessary
        # start = time.clock()
        # -> your code here <-
        # write debug info to a file
        # filehandle = open(filename, 'a')
        # filehandle.write(str(time.clock() - start) + "\r\n")
        # filehandle.close()

    def run(self):
        print "Client started, trying to connect to server"

        self.sock.connect(self._SERVER_INFO)

        print "Connected to server, creating video capture"

        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv.CV_CAP_PROP_FRAME_WIDTH, 320)
        self.capture.set(cv.CV_CAP_PROP_FRAME_HEIGHT, 240)

        print "Frame resolution set to: (" + str(self.capture.get(cv.CV_CAP_PROP_FRAME_WIDTH)) + "; " + str(self.capture.get(cv.CV_CAP_PROP_FRAME_HEIGHT)) + ")"

        # thread listening for params from the server
        params_listener = threading.Thread(target=self.get_params, args=())
        params_listener.daemon = True
        params_listener.start()

        # launch the whole process
        self.img_process()

        while True:

            # main loop
            key = cv2.waitKey(50)
            if key == 27:  # exit on ESC
                break
            if self.activation_level < 10:
                self.sample_time = 1
                self.gain = 2
            else:
                self.sample_time = 0.1
                self.gain = 0.1

        # if we ever get here ...
        self.sock.close()
        print "Client terminated"

client = VSNClient()
client.run()