# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_LeftWidget.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(260, 548)
        self.listWidget = QtWidgets.QListWidget(Form)
        self.listWidget.setGeometry(QtCore.QRect(16, 90, 231, 441))
        self.listWidget.setObjectName("listWidget")
        self.gridLayoutWidget = QtWidgets.QWidget(Form)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(20, 40, 221, 41))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.pB_add = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.pB_add.setObjectName("pB_add")
        self.gridLayout.addWidget(self.pB_add, 0, 0, 1, 1)
        self.pB_clear = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.pB_clear.setObjectName("pB_clear")
        self.gridLayout.addWidget(self.pB_clear, 0, 1, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.pB_add.setText(_translate("Form", "Add"))
        self.pB_clear.setText(_translate("Form", "Clear"))
