from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from ui.form.comport_setting_ui import Ui_Form_ComPortSetting
# from form.comport_setting_ui import Ui_Form_ComPortSetting
import serial.tools.list_ports
import serial

UART_TIMEOUT = 0.01

class ComPort():
    def __init__(self, combobox_comport:QComboBox, combobox_baudrate:QComboBox, button_connect:QPushButton):
        self.combobox_comport = combobox_comport
        self.combobox_baudrate = combobox_baudrate
        self.button_connect = button_connect

        self.comport = serial.Serial()

    def comport_ToggleConnect(self):
        if self.comport.is_open:
            self.comport.close()
            self.button_connect.setText("Disconnected")
            self.button_connect.setStyleSheet("background-color:rgb(255,204,204);font: 12pt 'Arial';")
        elif self.combobox_comport.currentText() != "":
            # Open COM Port
            self.comport.baudrate = int(self.combobox_baudrate.currentText())
            self.comport.port = self.combobox_comport.currentText()
            self.comport.timeout = UART_TIMEOUT
            self.comport.open()
            
            self.button_connect.setText("Connected")
            self.button_connect.setStyleSheet("background-color:rgb(204,239,220);font: 12pt 'Arial';")

    def updateComboBox(self):
        def isPortUsable(port_name:str):
            try:
                ser = serial.Serial(port_name)
                return True
            except:
                return False

        self.combobox_comport.clear()
        if self.comport.is_open:
            self.combobox_comport.addItem(self.comport.name)
        else:
            self.com_port_list = serial.tools.list_ports.comports()
            for com_port_item in self.com_port_list:
                if isPortUsable(com_port_item.name):
                    self.combobox_comport.addItem(com_port_item.name)

    def read_all(self):
        return self.comport.read_all()
    
    def flush(self):
        self.comport.flush()


class Uart(QWidget, Ui_Form_ComPortSetting):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.com_0 = ComPort(self.comboBox_ComPort0, self.comboBox_BaudRate0, self.pushButton_Connect0)
        self.com_1 = ComPort(self.comboBox_ComPort1, self.comboBox_BaudRate1, self.pushButton_Connect1)

        self.pushButton_Connect0.clicked.connect(self.button_comport0_connect)
        self.pushButton_Connect1.clicked.connect(self.button_comport1_connect)

    def show(self):
        self.com_0.updateComboBox()
        self.com_1.updateComboBox()
        return super().show()

    #
    #           Connection
    #
    def button_comport0_connect(self):
        self.com_0.comport_ToggleConnect()
        self.com_1.updateComboBox()

    def button_comport1_connect(self):
        self.com_1.comport_ToggleConnect()
        self.com_0.updateComboBox()

    #
    #           Functions
    #
    def readComport0(self):
        if self.com_0.comport.is_open:
            return self.com_0.read_all()
        return b""

    def readComport1(self):
        if self.com_1.comport.is_open:
            return self.com_1.read_all()
        return b""

    def flushComport0(self):
        self.com_0.flush()

    def flushComport1(self):
        self.com_1.flush()

    def switchComports(self):
        comport_temp = self.com_0.comport
        self.com_0.comport = self.com_1.comport
        self.com_1.comport = comport_temp

    def autoConnect(self):
        self.com_0.updateComboBox()
        self.com_0.comport_ToggleConnect()
        self.com_1.updateComboBox()
        self.com_1.comport_ToggleConnect()

    def getName_Com0(self):
        return self.com_0.comport.name

    def getName_Com1(self):
        return self.com_1.comport.name

###################################################
#                   Main function
###################################################
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = Uart()
    w.show()
    sys.exit(app.exec_())


