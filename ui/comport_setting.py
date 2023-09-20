from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from enum import Enum

from ui.form.comport_setting_ui import Ui_Form_ComPortSetting
# from form.comport_setting_ui import Ui_Form_ComPortSetting
import serial.tools.list_ports
import serial

UART_TIMEOUT = 0.01

class Console(Enum):
    INDEX_0 = 0x01
    INDEX_1 = 0x02
    INDEX_ALL = INDEX_0 or INDEX_1

class ComPort():
    def __init__(self, combobox_comport:QComboBox, combobox_baudrate:QComboBox, button_connect:QPushButton):
        self.combobox_comport = combobox_comport
        self.combobox_baudrate = combobox_baudrate
        self.button_connect = button_connect

        self.comport = serial.Serial()

        # self.combobox_comport.activated.connect(self.combobox_activated_update)
        # self.combobox_comport.view().pressed.connect(self.combobox_activated_update)

    def comport_ToggleConnect(self):
        print(f"com = {self.combobox_comport.currentText()}")
        if not self.isExist(self.combobox_comport.currentText()):
            print(f"com doesn't exist")
            self.combobox_comport.removeItem(self.combobox_comport.currentIndex())
            # self.combobox_comport.setCurrentText("")
            self.close()
        elif self.comport.is_open:
            print(f"com is going to close")
            self.close()
        elif self.combobox_comport.currentText() != "":
            print(f"com is going to open")
            self.open()

    def _isPortUsable(self, port_name:str)->bool:
        try:
            ser = serial.Serial(port_name)
            return True
        except:
            return False

    def updateComboBox(self):

        self.combobox_comport.clear()
        if self.comport.is_open:
            self.combobox_comport.addItem(self.comport.name)
        else:
            # for com_port_item in serial.tools.list_ports.comports():
            #     if self._isPortUsable(com_port_item.name):
            #         self.combobox_comport.addItem(com_port_item.name)
            for com_port_name in self.getComNameList():
                if self._isPortUsable(com_port_name):
                    self.combobox_comport.addItem(com_port_name)

    def getComNameList(self):
        # comport_name_list = [comport.name for comport in serial.tools.list_ports.comports()]
        # comport_desc_list = [comport.description for comport in serial.tools.list_ports.comports()]
        # print(f"comport_desc_list = {comport_desc_list}")
        comport_name_list = []
        for com_port in serial.tools.list_ports.comports():
            if "JLink" not in com_port.description:
                comport_name_list.append(com_port.name)
        return comport_name_list

    def read_all(self):
        return self.comport.read_all()
    
    def flush(self):
        self.comport.flush()

    def open(self):
        if not self.comport.is_open and self._isPortUsable(self.combobox_comport.currentText()):
            self.comport.baudrate = int(self.combobox_baudrate.currentText())
            self.comport.port = self.combobox_comport.currentText()
            self.comport.timeout = UART_TIMEOUT
            self.comport.open()

        if self.comport.is_open:
            self.combobox_comport.setEnabled(False)
            self.button_connect.setText("Connected")
            self.button_connect.setStyleSheet("background-color:rgb(204,239,220);font: 12pt 'Arial';")
        else:
            self.combobox_comport.setEnabled(True)
            self.button_connect.setText("Disconnected")
            self.button_connect.setStyleSheet("background-color:rgb(255,204,204);font: 12pt 'Arial';")

    def close(self):
        self.combobox_comport.setEnabled(True)
        self.button_connect.setText("Disconnected")
        self.button_connect.setStyleSheet("background-color:rgb(255,204,204);font: 12pt 'Arial';")
        if not self.comport.is_open:
            return
        self.comport.close()
        self.updateComboBox()

    def is_open(self):
        return self.comport.is_open

    def isExist(self, comport_name:str):
        comport_name_list = self.getComNameList()
        print(f"isExist: comport_name = {comport_name}, list = {comport_name_list}")
        return comport_name in comport_name_list
    
class Uart(QWidget, Ui_Form_ComPortSetting):
    signal_update_uart = pyqtSignal()
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
    
    def closeEvent(self, a0: QCloseEvent) -> None:
        self.signal_update_uart.emit()
        print(f"close uart setting")
        return super().closeEvent(a0)

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

    def autoConnect(self, comport_index = Console.INDEX_ALL)->int:
        com_num = 0

        if comport_index == Console.INDEX_0 or comport_index == Console.INDEX_ALL:
            self.com_0.updateComboBox()
            self.com_0.open()
            if self.com_0.is_open():
                com_num = com_num + 1

        if comport_index == Console.INDEX_1 or comport_index == Console.INDEX_ALL:
            self.com_1.updateComboBox()
            self.com_1.open()
            if self.com_1.is_open():
                com_num = com_num + 1

        return com_num

    def getName_Com0(self):
        return self.com_0.comport.name

    def getName_Com1(self):
        return self.com_1.comport.name
    
    def close_Com0(self):
        return self.com_0.close()

    def close_Com1(self):
        return self.com_1.close()

###################################################
#                   Main function
###################################################
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = Uart()
    w.show()
    sys.exit(app.exec_())


