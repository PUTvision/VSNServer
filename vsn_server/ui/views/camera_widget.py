# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'camera_widget.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CameraWidget(object):
    def setupUi(self, CameraWidget):
        CameraWidget.setObjectName("CameraWidget")
        CameraWidget.resize(400, 300)
        self.gridLayout = QtWidgets.QGridLayout(CameraWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.preview = QtWidgets.QLabel(CameraWidget)
        self.preview.setText("")
        self.preview.setObjectName("preview")
        self.gridLayout.addWidget(self.preview, 0, 0, 1, 1)

        self.retranslateUi(CameraWidget)
        QtCore.QMetaObject.connectSlotsByName(CameraWidget)

    def retranslateUi(self, CameraWidget):
        _translate = QtCore.QCoreApplication.translate
        CameraWidget.setWindowTitle(_translate("CameraWidget", "Form"))

