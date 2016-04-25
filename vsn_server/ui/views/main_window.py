# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_VSNServer(object):
    def setupUi(self, VSNServer):
        VSNServer.setObjectName("VSNServer")
        VSNServer.resize(953, 673)
        self.centralwidget = QtWidgets.QWidget(VSNServer)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.mostActiveCamerasGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.mostActiveCamerasGroupBox.setObjectName("mostActiveCamerasGroupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.mostActiveCamerasGroupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.mostActivePreview3 = QtWidgets.QGraphicsView(self.mostActiveCamerasGroupBox)
        self.mostActivePreview3.setObjectName("mostActivePreview3")
        self.gridLayout_2.addWidget(self.mostActivePreview3, 0, 0, 1, 1)
        self.mostActivePreview1 = QtWidgets.QGraphicsView(self.mostActiveCamerasGroupBox)
        self.mostActivePreview1.setObjectName("mostActivePreview1")
        self.gridLayout_2.addWidget(self.mostActivePreview1, 0, 2, 1, 1)
        self.mostActivePreview2 = QtWidgets.QGraphicsView(self.mostActiveCamerasGroupBox)
        self.mostActivePreview2.setObjectName("mostActivePreview2")
        self.gridLayout_2.addWidget(self.mostActivePreview2, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.mostActiveCamerasGroupBox, 0, 0, 1, 1)
        self.allCamerasGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.allCamerasGroupBox.setObjectName("allCamerasGroupBox")
        self.allCamerasLayout = QtWidgets.QGridLayout(self.allCamerasGroupBox)
        self.allCamerasLayout.setObjectName("allCamerasLayout")
        self.gridLayout.addWidget(self.allCamerasGroupBox, 1, 0, 1, 1)
        VSNServer.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(VSNServer)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 953, 30))
        self.menubar.setObjectName("menubar")
        self.menuVSN = QtWidgets.QMenu(self.menubar)
        self.menuVSN.setObjectName("menuVSN")
        VSNServer.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(VSNServer)
        self.statusbar.setObjectName("statusbar")
        VSNServer.setStatusBar(self.statusbar)
        self.actionClose = QtWidgets.QAction(VSNServer)
        self.actionClose.setObjectName("actionClose")
        self.menuVSN.addAction(self.actionClose)
        self.menubar.addAction(self.menuVSN.menuAction())

        self.retranslateUi(VSNServer)
        self.actionClose.triggered.connect(VSNServer.close)
        QtCore.QMetaObject.connectSlotsByName(VSNServer)

    def retranslateUi(self, VSNServer):
        _translate = QtCore.QCoreApplication.translate
        VSNServer.setWindowTitle(_translate("VSNServer", "MainWindow"))
        self.mostActiveCamerasGroupBox.setTitle(_translate("VSNServer", "Most active cameras"))
        self.allCamerasGroupBox.setTitle(_translate("VSNServer", "All cameras"))
        self.menuVSN.setTitle(_translate("VSNServer", "VS&NServer"))
        self.actionClose.setText(_translate("VSNServer", "&Close"))

