# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/form/com2_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ComPortWindow(object):
    def setupUi(self, ComPortWindow):
        ComPortWindow.setObjectName("ComPortWindow")
        ComPortWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(ComPortWindow)
        self.centralwidget.setObjectName("centralwidget")
        ComPortWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(ComPortWindow)
        self.statusbar.setObjectName("statusbar")
        ComPortWindow.setStatusBar(self.statusbar)

        self.retranslateUi(ComPortWindow)
        QtCore.QMetaObject.connectSlotsByName(ComPortWindow)

    def retranslateUi(self, ComPortWindow):
        _translate = QtCore.QCoreApplication.translate
        ComPortWindow.setWindowTitle(_translate("ComPortWindow", "Two Com Ports"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ComPortWindow = QtWidgets.QMainWindow()
    ui = Ui_ComPortWindow()
    ui.setupUi(ComPortWindow)
    ComPortWindow.show()
    sys.exit(app.exec_())
