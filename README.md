# cam_network
This code is used in the project entitled:

*"NEW CONCEPT OF THE NETWORK OF SMART CAMERAS WITH ENHANCED AUTONOMY FOR AUTOMATIC SURVEILLANCE SYSTEM"*

More information about the project can be found: http://www.vision.put.poznan.pl/?page_id=237

# Project in a nutshell
The aim of the provided code is to test the algorithms for controlling the network of smart cameras.

Each camera node is based on RaspberryPi board which is handling all the processing. Based on the motion detected on the observed scene, the camera is changing how frequently it captures the image and do the processing. In addition to that the current activity level is propagated to neighbouring nodes (through central server) which also influence how active each camera is.

Such solution enables to put most of the camera in the system into low power mode, and do the image processing relatively infrequently. As a result the whole system is saving power which can enable it to operate on battery. On the other hand thanks to the propagation of information about motion between cameras no important information is lost.

# Languages and tools used
Project is written in Python 2.7 and uses following libraries (+ all the prequisitions for those):
* opencv - for image acquisition processing tasks,
* twisted - for networking,
* pyqtgraph - for plotting.

# Running the code
Copy the repository to RaspberryPi (git clone) board and download ale the libraries required. If you already have the repository, do just git pull. Change the hostname of the RPi to one of the following: picam01, picam02, picam03, picam04, picam05.

Start the server (server_qt) on the central node (should be 192.168.0.10 IP address), and then start camera (picam_generic) on each RPi.

# Modules description
Common:
* VSNPacket
* VSNUtility

Server:
* server_qt
  * qt4reactor
  * VSNServer
  * VSNGraph
  * VSNCameraData

Picam:
* VSNPicam
  * VSNClient
  * VSNActivityController
  * VSNImageProcessing

Tests:
* picam_generic
* picam01
* picam02

# Future changes

# Useful links
