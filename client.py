import socket
import cv2
import numpy
import cv2.cv as cv
import math
import time
import threading

TCP_IP = '192.168.0.100'
TCP_PORT = 5001

sock = socket.socket()
sock.connect((TCP_IP, TCP_PORT))
capture = cv2.VideoCapture(0)

capture.set(cv.CV_CAP_PROP_FRAME_WIDTH, 320)
capture.set(cv.CV_CAP_PROP_FRAME_HEIGHT, 240)

lock = threading.Lock()

# let the camera adjust the auto parameters (gain etc.) on a few images
for x in range(0, 15):
    ret, frame = capture.read()
background = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
struct = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

print "Frame resolution set to: (" + str(capture.get(cv.CV_CAP_PROP_FRAME_WIDTH)) + "; " + str(
    capture.get(cv.CV_CAP_PROP_FRAME_HEIGHT)) + ")"
print "Client running, press ESC to quit"

filename = "log.csv"            # log file name - if logging is enabled
activation_level = 0            # default starting activation level
sample_time = 0.1               # sample time at startup
gain = 0.1                      # gain at startup
flag_senddata = False           # default behavior - do not send the image data

# lowpass filter function modelled after a 1st order inertial object transformed using delta minus method
def lowpass(prev_sample, input_val, sample_time_lowpass):
    time_constant = 1
    output = (gain / time_constant) * input_val + prev_sample * pow(math.e, -1.0 * (sample_time_lowpass / time_constant))
    return output


def img_process():

    lock.acquire()

    global background, activation_level, data, percentage, sample_time

    # wait for slackers to finish
    while threading.active_count() > 3:
        time.sleep(0.01)

    #queue a call to itself after sample time has elapsed to ensure periodic firing
    threading.Timer(sample_time, img_process).start()

    # grab and process frame, update the background and foreground model
    ret, frame = capture.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mask_gt = cv2.compare(background, gray, cv2.CMP_GT)
    mask_lt = cv2.compare(background, gray, cv2.CMP_LT)

    background += mask_lt / 128.0
    background -= mask_gt / 128.0

    difference = cv2.absdiff(background, gray)
    difference = cv2.medianBlur(difference, 3)
    display = cv2.compare(difference, 6, cv2.CMP_GT)
    eroded = cv2.erode(display, struct)
    dilated = cv2.dilate(eroded, struct)
    nonzero = cv2.countNonZero(dilated)

    height, width = dilated.shape[:2]
    percentage = (nonzero * 100 / (height * width))

    # compute the sensor state based on captured images
    activation_level_new = lowpass(activation_level, percentage, sample_time)
    activation_level = activation_level_new

    ##### TODO: implement functionality allowing to choose whether or not to send the image of choice (fg, bg, raw)

    # encode image for sending 
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    result, imgencode = cv2.imencode('.jpg', dilated, encode_param)
    data = numpy.array(imgencode)

    string_data = data.tostring()

    ###### to do ends here

    # send the obligatory sensor state info
    sock.send(socket.gethostname().ljust(8))
    sock.send(str(percentage).ljust(32))
    sock.send(str(activation_level).ljust(32))
    sock.send(str(len(string_data)).ljust(32))
    sock.send(string_data)

    lock.release()


    # simple profiling, uncomment if necessary
    # start = time.clock()
    # -> your code here <-
    # write debug info to a file
    # filehandle = open(filename, 'a')
    # filehandle.write(str(time.clock() - start) + "\r\n")
    # filehandle.close()

# launch the whole process
img_process()

while True:

    # main loop
    # TODO: add the change of sample time based on activity level
    key = cv2.waitKey(50)
    if key == 27:  # exit on ESC
        break
    if activation_level < 10:
        sample_time = 1
        gain = 2
    else:
        sample_time = 0.1
        gain = 0.1

# if we ever get here ...
sock.close()
print "Client terminated"

