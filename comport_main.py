from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QRegExp

import comport_ui as ui

import serial.tools.list_ports

###################################################
#                   Constant
###################################################
UART_TIMEOUT = 0.1
READ_MSG_NUM = 200
INPUT_MASK_HEX = "HH HH HH HH HH HH HH HH HH HH HH HH HH HH HH HH \
HH HH HH HH HH HH HH HH HH HH HH HH HH HH HH HH;_"
INPUT_MASK_NONE = ""

###################################################
#                   Main class
###################################################
class Main(QMainWindow, ui.Ui_MainForm):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        self.groupBox_Tx.setEnabled(False)
        
        # Serial port setting
        self.pushButton_Connect.clicked.connect(self.Button_Connect) 
        self.Comport_Set()
        
        # self.comboBox_ComPort.setEditable(True)
        # self.comboBox_ComPort.lineEdit().setAlignment(Qt.AlignCenter)
        # self.comboBox_ComPort.lineEdit().setReadOnly(True)
        
        # Serial port receiver with timer
        self.comport_timer = QTimer(self)
        self.comport_timer.timeout.connect(self.Timer_UartRx)

        # Setting button
        self.pushButton_Clear.clicked.connect(self.Button_Clear)
        self.pushButton_Stop.clicked.connect(self.Button_Stop)
        
        self.pushButton_Tx_Send.clicked.connect(self.Button_Tx_Send)
        self.pushButton_Tx_Clear.clicked.connect(self.Button_Tx_Clear)
        
        self.spinBox_FontSize.valueChanged.connect(self.SpinBox_FontSize_Set)
        
        # If only one com port, connect it directly
        if self.comboBox_ComPort.count() == 1:
            self.Button_Connect()
                
        self.radioButton_Hex.toggled.connect(self.Radio_Text_Type)
        self.radioButton_Ascii.toggled.connect(self.Radio_Text_Type)

                
    #--------------------------------------------------
    #           MainForm virtual function
    #--------------------------------------------------
    def resizeEvent(self, event):
    
        self.TextEdit_Resize()
        
        # Get current MainForm size
        mainform_width = self.frameGeometry().width()
        mainform_height = self.frameGeometry().height()

        # Set groupBox_Tx position
        groupBox_Tx_x = self.groupBox_Tx.frameGeometry().x()
        groupBox_Tx_y = (mainform_height - 30) - self.groupBox_Tx.frameGeometry().height() - 30
        self.groupBox_Tx.move(groupBox_Tx_x, groupBox_Tx_y)

        # reg=QRegExp('[a-fA-F0-9]{,2}[ ]')
        # validator = QRegExpValidator(self)
        # validator.setRegExp(reg)
        # self.lineEdit_Tx.setValidator(validator)        
        
        self.lineEdit_Tx.setInputMask(INPUT_MASK_HEX)

        # self.radioButton_Hex.toggled.connect(self.Radio_Text_Type)
        # self.radioButton_Ascii.toggled.connect(self.Radio_Text_Type)

    # def mousePressEvent(self, event):
        # if event.button() == Qt.LeftButton:
            # p = self.mapFromGlobal(QCursor.pos())
            # self.textEdit_hex.append('(%d , %d)'%(p.x(),p.y()))
               
    #--------------------------------------------------
    #               Object Connection
    #--------------------------------------------------
    def Button_Connect(self):
        if self.pushButton_Connect.text() == "Disconnected":
            # Open COM Port
            self.comport_sel = serial.Serial()
            self.comport_sel.baudrate = int(self.comboBox_BaudRate.currentText())
            self.comport_sel.port = self.comboBox_ComPort.currentText()
            self.comport_sel.timeout = UART_TIMEOUT
            self.comport_sel.open()
            
            self.groupBox_Tx.setEnabled(True)
            self.pushButton_Connect.setText("Connected")
            self.pushButton_Connect.setStyleSheet("background-color:rgb(204,239,220);font: 12pt 'Arial';")
            # self.comport_timer.start(200)
            self.Comport_Read("Reading")
        else:
            # self.comport_timer.stop()
            self.Comport_Read("Stopped")
            self.comport_sel.close()
            self.groupBox_Tx.setEnabled(False)
            self.pushButton_Connect.setText("Disconnected")
            self.pushButton_Connect.setStyleSheet("background-color:rgb(255,204,204);font: 12pt 'Arial';")

    def Button_Clear(self):
        self.textEdit_ascii.clear()
        self.textEdit_hex.clear()
        
        # mainform_width = self.frameGeometry().width()
        # mainform_height = self.frameGeometry().height()
        # groupBox_Tx_height = self.groupBox_Tx.frameGeometry().height()
        # groupBox_Tx_y = self.groupBox_Tx.frameGeometry().y()
        
        # self.textEdit_hex.append("width = " + str(mainform_width) + "height = " + str(mainform_height))
        # self.textEdit_hex.append("groupBox_Tx_height = " + str(groupBox_Tx_height) + "groupBox_Tx_y = " + str(groupBox_Tx_y))
        
    def Button_Stop(self):
        if self.pushButton_Stop.text() == "Stopped":
            self.Comport_Read("Reading")
        else:
            self.Comport_Read("Stopped")
        
    def Button_Tx_Send(self):
        if self.radioButton_Hex.isChecked():
            send_msg_list = self.lineEdit_Tx.text().split()
            send_msg = ""
            for hex_string in send_msg_list:
                send_msg += hex_string.zfill(2)
            self.comport_sel.write(bytearray.fromhex(send_msg))
        else:
            self.comport_sel.write(self.lineEdit_Tx.text().encode())
        pass
        
    def Button_Tx_Clear(self):
        self.lineEdit_Tx.clear()
        pass
        
    def Radio_Text_Type(self):
        # radioBtn = self.sender()
        if self.sender() == self.radioButton_Hex and self.radioButton_Hex.isChecked():
            print("hex")
            self.label_Tx_HexNum.setVisible(True)
            self.lineEdit_Tx.setInputMask(INPUT_MASK_HEX)
        elif self.sender() == self.radioButton_Ascii and self.radioButton_Ascii.isChecked():
            print("ascii")
            self.label_Tx_HexNum.setVisible(False)
            self.lineEdit_Tx.setInputMask(INPUT_MASK_NONE)
        pass
        
        self.TextEdit_Resize()
    
    def SpinBox_FontSize_Set(self):
        self.textEdit_ascii.setFontPointSize(self.spinBox_FontSize.value())
        self.textEdit_hex.setFontPointSize(self.spinBox_FontSize.value())
        label_HexPos_font = self.label_HexPos.font()
        label_HexPos_font.setPointSize(self.spinBox_FontSize.value())
        self.label_HexPos.setFont(label_HexPos_font)
        pass
    #--------------------------------------------------
    #                       Timer
    #--------------------------------------------------
    def Timer_UartRx(self):
        print_ascii = ""
        print_hex = ""

        while True:
            read_msg = self.comport_sel.read(READ_MSG_NUM)
            if len(read_msg) == 0:
                if len(print_ascii):
                    self.textEdit_ascii.append(print_ascii)
                if len(print_hex):
                    self.textEdit_hex.append(print_hex)
                return
                
            for read_byte in read_msg:
                if self.radioButton_Hex.isChecked():
                    if read_byte < 0x20 or read_byte > 0x7F:
                        print_ascii += '.'
                        print_hex += hex(read_byte)[2:].zfill(2) + " "
                    else:
                        print_ascii += chr(read_byte)
                        print_hex += hex(read_byte)[2:].zfill(2) + " "                
                else:
                    if read_byte == 0x0D or read_byte == 0x0A:
                        # print_ascii += chr(read_byte)
                        print_hex += hex(read_byte)[2:].zfill(2) + " "
                        if read_byte == 0x0A:
                            self.textEdit_ascii.append(print_ascii)
                            self.textEdit_hex.append(print_hex)
                            print_ascii = ""
                            print_hex = ""
                    elif read_byte < 0x20 or read_byte > 0x7F:
                        print_ascii += '.'
                        print_hex += hex(read_byte)[2:].zfill(2) + " "
                    else:
                        print_ascii += chr(read_byte)
                        print_hex += hex(read_byte)[2:].zfill(2) + " "                
        
    #--------------------------------------------------
    #               Function implement
    #--------------------------------------------------
    def Comport_Set(self):
        comlist = serial.tools.list_ports.comports()
        connected = []
        for element in sorted(comlist):
            connected.append(element.device)
        self.comboBox_ComPort.addItems(connected)
        # if len(connected) == 1:
            # self.Button_Connect()

    def Comport_Read(self, str_action):
        if str_action == "Reading":
            self.pushButton_Stop.setText("Reading")
            self.pushButton_Stop.setStyleSheet(";background-color:rgb(204,239,220);font: 12pt 'Arial';")
            self.comport_sel.flushInput()
            self.comport_timer.start(200)
        else:
            self.pushButton_Stop.setText("Stopped")
            self.pushButton_Stop.setStyleSheet("background-color:rgb(255,204,204);font: 12pt 'Arial';")
            self.comport_timer.stop()

    def TextEdit_Resize(self):
        # Get current MainForm size
        mainform_width = self.frameGeometry().width()
        mainform_height = self.frameGeometry().height()

        if self.radioButton_Hex.isChecked():
            self.textEdit_hex.setVisible(True)
            # Set textEdit_hex size
            textEdit_hex_width = (mainform_width - self.groupBox_Comport.frameGeometry().width() - 10 - 10 - 10 - 10) * 3 / 4
            textEdit_hex_height = (mainform_height - 30) - self.groupBox_Tx.frameGeometry().height() - 30 - 20 - 10
            self.textEdit_hex.resize(textEdit_hex_width, textEdit_hex_height)
            
            label_HexPos_width = textEdit_hex_width
            self.label_HexPos.resize(label_HexPos_width, self.label_HexPos.frameGeometry().height())
            
            # Set textEdit_ascii position and size
            textEdit_ascii_width = (mainform_width - self.groupBox_Comport.frameGeometry().width() - 10 - 10 - 10 - 10) * 1 / 4
            textEdit_ascii_height = (mainform_height - 30) - self.groupBox_Tx.frameGeometry().height() - 30 - 20 - 10
            textEdit_ascii_x = mainform_width - 10 - textEdit_ascii_width
            textEdit_ascii_y = self.textEdit_ascii.frameGeometry().y()
            self.textEdit_ascii.move(textEdit_ascii_x, textEdit_ascii_y)
            self.textEdit_ascii.resize(textEdit_ascii_width, textEdit_ascii_height)
            
        else:
            self.textEdit_hex.setVisible(False)
            # Set textEdit_ascii position and size
            textEdit_ascii_width = (mainform_width - self.groupBox_Comport.frameGeometry().width() - 10 - 10 - 10 - 10)
            textEdit_ascii_height = (mainform_height - 30) - self.groupBox_Tx.frameGeometry().height() - 30 - 20 - 10
            textEdit_ascii_x = mainform_width - textEdit_ascii_width - 20
            textEdit_ascii_y = self.textEdit_ascii.frameGeometry().y()
            self.textEdit_ascii.move(textEdit_ascii_x, textEdit_ascii_y)
            self.textEdit_ascii.resize(textEdit_ascii_width, textEdit_ascii_height)




###################################################
#                   Main function
###################################################
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())