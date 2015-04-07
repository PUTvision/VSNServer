__author__ = 'Amin'

from VSNImageProcessing import VSNImageProcessing
from VSNImageProcessing import VSNActivityController
from VSNClient import VSNClientFactory
from VSNPacket import VSNPacket

from twisted.internet import reactor
from twisted.internet import task

import cv2

import numpy

import socket


def ragular_updates():
    percentage_of_nonzero_pixels = VSN_image_processor.do_image_processing()
    VSN_activity_controller.update_sensor_state_based_on_captured_image(percentage_of_nonzero_pixels)
    cv2.imshow('fg', VSN_image_processor._background_image)
    print "Params: " + \
          str(VSN_activity_controller.activation_level) + \
          ", " + \
          str(VSN_activity_controller.gain) + \
          ", " +\
          str(VSN_activity_controller.sample_time) + \
          "\r\n"
    cv2.waitKey(1)
    VSN_packet.set(
        node_number,
        percentage_of_nonzero_pixels,
        VSN_activity_controller.activation_level,
        False
    )
    VSN_client_factory.send_packet(VSN_packet)

    # encode image for sending
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    result, imgencode = cv2.imencode('.jpg', VSN_image_processor._background_image, encode_param)
    data = numpy.array(imgencode)

    image_as_string = data.tostring()

    #VSN_client_factory.send_image(image_as_string)

if __name__ == '__main__':

    # constant definitions
    #SERVER_IP = '192.168.0.100'
    SERVER_IP = '127.0.0.1'
    SERVER_PORT = 50001

    print 'picamXX length: ', len("picamXX")

    node_name = socket.gethostname()
    node_number = 3
    if len(node_name) == 7:
        if node_name[5:6].isdigit():
            node_number = int(node_name[5:6])

    print node_number

    # create factory protocol and application
    VSN_client_factory = VSNClientFactory()
    VSN_image_processor = VSNImageProcessing()
    VSN_activity_controller = VSNActivityController()
    VSN_packet = VSNPacket()
    VSN_packet.camera_number = node_number

    # connect factory to this host and port
    reactor.connectTCP(SERVER_IP, SERVER_PORT, VSN_client_factory)

    l = task.LoopingCall(ragular_updates)
    l.start(0.1)  # call every 1/10 second

    # run bot
    reactor.run()