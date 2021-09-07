from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QRegExp

import comport_window_ui as ui

import serial.tools.list_ports
from datetime import datetime

###################################################
#                   Constant
###################################################

TX_TYPE_HEX = 0
TX_TYPE_ASCII = 1

UART_TIMEOUT = 0.1
READ_MSG_NUM = 200
INPUT_MASK_HEX = "HH HH HH HH HH HH HH HH HH HH HH HH HH HH HH HH \
HH HH HH HH HH HH HH HH HH HH HH HH HH HH HH HH;_"
INPUT_MASK_NONE = ""

###################################################
#                   Main class
###################################################
class Main(QMainWindow, ui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        self.groupBox_Tx.setEnabled(False)
        
        self.focus_object = None
        
        self.textEdit_ascii.setWordWrapMode(QTextOption.WrapAnywhere)
        
        # Serial port setting
        self.pushButton_Connect.clicked.connect(self.button_Connect) 
        self.comport_Set()
        
        # self.comboBox_ComPort.setEditable(True)
        # self.comboBox_ComPort.lineEdit().setAlignment(Qt.AlignCenter)
        # self.comboBox_ComPort.lineEdit().setReadOnly(True)
        
        # Serial port receiver with timer
        self.comport_timer = QTimer(self)
        self.comport_timer.timeout.connect(self.timer_UartRx)

        # Setting button
        self.pushButton_Clear.clicked.connect(self.button_Clear)
        self.pushButton_Stop.clicked.connect(self.button_Stop)
        
        self.pushButton_Tx_Send.clicked.connect(self.button_Tx_Send)
        self.pushButton_Tx_Clear.clicked.connect(self.button_Tx_Clear)
        
        self.spinBox_FontSize.valueChanged.connect(self.spinBox_FontSize_Set)
        
        # If only one com port, connect it directly
        if self.comboBox_ComPort.count() == 1:
            self.button_Connect()
                       
        self.textEdit_ascii.verticalScrollBar().valueChanged.connect(self.textEdit_hex.verticalScrollBar().setValue)
        self.textEdit_hex.verticalScrollBar().valueChanged.connect(self.textEdit_ascii.verticalScrollBar().setValue)

        self.textEdit_hex.selectionChanged.connect(self.textEdit_hex_selectionChanged)
        self.textEdit_ascii.selectionChanged.connect(self.textEdit_ascii_selectionChanged)
        
        QtWidgets.qApp.focusChanged.connect(self.mainWindow_FocusChanged)
        
        self.action_Text_Ascii.triggered.connect(self.action_textWindow)
        self.action_Text_Hex.triggered.connect(self.action_textWindow)
        
        self.action_Tx_Ascii.triggered.connect(self.action_txType)
        self.action_Tx_Hex.triggered.connect(self.action_txType)
                
    #--------------------------------------------------
    #           MainForm virtual function
    #--------------------------------------------------
    def resizeEvent(self, event):
    
        self.textEdit_Resize()
        
        # Get current MainForm size
        mainform_width = self.frameGeometry().width()
        mainform_height = self.frameGeometry().height()

        # Set groupBox_Tx position
        groupBox_Tx_x = self.groupBox_Tx.frameGeometry().x()
        groupBox_Tx_y = (mainform_height - 30) - self.groupBox_Tx.frameGeometry().height() - 50
        self.groupBox_Tx.move(groupBox_Tx_x, groupBox_Tx_y)

        # reg=QRegExp('[a-fA-F0-9]{,2}[ ]')
        # validator = QRegExpValidator(self)
        # validator.setRegExp(reg)
        # self.lineEdit_Tx.setValidator(validator)        
        
        self.lineEdit_Tx.setInputMask(INPUT_MASK_HEX)

    # def mousePressEvent(self, event):
        # if event.button() == Qt.LeftButton:
            # p = self.mapFromGlobal(QCursor.pos())
            # self.textEdit_hex.append('(%d , %d)'%(p.x(),p.y()))
               
    #--------------------------------------------------
    #               Object Connection
    #--------------------------------------------------
    def button_Connect(self):
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
            self.comport_Read("Reading")
        else:
            # self.comport_timer.stop()
            self.comport_Read("Stopped")
            self.comport_sel.close()
            self.groupBox_Tx.setEnabled(False)
            self.pushButton_Connect.setText("Disconnected")
            self.pushButton_Connect.setStyleSheet("background-color:rgb(255,204,204);font: 12pt 'Arial';")

    def button_Clear(self):
        self.textEdit_ascii.clear()
        self.textEdit_hex.clear()
        
        # mainform_width = self.frameGeometry().width()
        # mainform_height = self.frameGeometry().height()
        # groupBox_Tx_height = self.groupBox_Tx.frameGeometry().height()
        # groupBox_Tx_y = self.groupBox_Tx.frameGeometry().y()
        
        # self.textEdit_hex.append("width = " + str(mainform_width) + "height = " + str(mainform_height))
        # self.textEdit_hex.append("groupBox_Tx_height = " + str(groupBox_Tx_height) + "groupBox_Tx_y = " + str(groupBox_Tx_y))
        
    def button_Stop(self):
        if self.pushButton_Stop.text() == "Stopped":
            self.comport_Read("Reading")
        else:
            self.comport_Read("Stopped")
        
    def button_Tx_Send(self):
        if self.action_Text_Hex.isChecked():
            send_msg_list = self.lineEdit_Tx.text().split()
            send_msg = ""
            for hex_string in send_msg_list:
                send_msg += hex_string.zfill(2)
            self.comport_sel.write(bytearray.fromhex(send_msg))
        else:
            self.comport_sel.write(self.lineEdit_Tx.text().encode())
        pass
        
    def button_Tx_Clear(self):
        self.lineEdit_Tx.clear()
        pass
        
    # def Radio_Text_Type(self):      
        # self.textEdit_Resize()
    
    # def Radio_Tx_Type(self):
        # if self.sender() == self.action_Text_Hex and self.action_Text_Hex.isChecked():
            # # print("hex")
            # self.label_Tx_HexNum.setVisible(True)
            # self.lineEdit_Tx.setInputMask(INPUT_MASK_HEX)
        # elif self.sender() == self.action_Text_Ascii and self.action_Text_Ascii.isChecked():
            # # print("ascii")
            # self.label_Tx_HexNum.setVisible(False)
            # self.lineEdit_Tx.setInputMask(INPUT_MASK_NONE)
        # pass    
    
    
    def spinBox_FontSize_Set(self):
        self.textEdit_ascii.setFontPointSize(self.spinBox_FontSize.value())
        self.textEdit_hex.setFontPointSize(self.spinBox_FontSize.value())
        label_HexPos_font = self.label_HexPos.font()
        label_HexPos_font.setPointSize(self.spinBox_FontSize.value())
        self.label_HexPos.setFont(label_HexPos_font)
        pass

    def textEdit_hex_selectionChanged(self):
    
        if self.focus_object != self.textEdit_hex:
            return
    
        cursor = self.textEdit_hex.textCursor()  
    
        start = (cursor.selectionStart() + cursor.blockNumber() * 2) / 3
        end = (cursor.selectionEnd() + cursor.blockNumber() * 2) / 3
    
        textEdit_ascii_cursor = self.textEdit_hex.textCursor()
        textEdit_ascii_cursor.setPosition(start) 
        textEdit_ascii_cursor.setPosition(end, QTextCursor.KeepAnchor) 
        self.textEdit_ascii.setTextCursor(textEdit_ascii_cursor)
    
    def textEdit_ascii_selectionChanged(self):
    
        if self.focus_object != self.textEdit_ascii:
            return
    
        cursor = self.textEdit_ascii.textCursor()  
    
        start = cursor.selectionStart() * 3 - cursor.blockNumber() * 2
        end = cursor.selectionEnd() * 3 - cursor.blockNumber() * 2
    
        textEdit_hex_cursor = self.textEdit_hex.textCursor()
        textEdit_hex_cursor.setPosition(start) 
        textEdit_hex_cursor.setPosition(end, QTextCursor.KeepAnchor) 
        self.textEdit_hex.setTextCursor(textEdit_hex_cursor)

    def mainWindow_FocusChanged(self, old, now):

        if now == self.textEdit_hex:
            self.focus_object = self.textEdit_hex
            print("textEdit_hex")
        elif now == self.textEdit_ascii:
            self.focus_object = self.textEdit_ascii
            print("textEdit_ascii")
        else:
            self.focus_object = None
            print("None")
        
    def action_textWindow(self):
        if self.sender() == self.action_Text_Hex:
            if self.action_Text_Hex.isChecked():
                print("action_textWindow - Hex")
                self.action_Text_Ascii.setChecked(False)
            else:
                print("action_textWindow - Ascii")
                self.action_Text_Ascii.setChecked(True)
                self.action_Text_Hex.setChecked(False)
        elif self.sender() == self.action_Text_Ascii:
            if self.action_Text_Ascii.isChecked():
                print("action_textWindow - Ascii")
                self.action_Text_Hex.setChecked(False)
            else:
                print("action_textWindow - Hex")
                self.action_Text_Hex.setChecked(True)
                self.action_Text_Ascii.setChecked(False)
        self.textEdit_Resize()

    def action_txType(self):
        if self.sender() == self.action_Tx_Hex:
            if self.action_Tx_Hex.isChecked():
                print("action_txType - Hex")
                self.action_Tx_Ascii.setChecked(False)
                self.txType_Set(TX_TYPE_HEX)
            else:
                print("action_txType - Ascii")            
                self.action_Tx_Hex.setChecked(False)
                self.action_Tx_Ascii.setChecked(True)
                self.txType_Set(TX_TYPE_ASCII)
        elif self.sender() == self.action_Tx_Ascii:
            if self.action_Tx_Ascii.isChecked():
                print("action_txType - Ascii")
                self.action_Tx_Hex.setChecked(False)
                self.txType_Set(TX_TYPE_ASCII)
            else:
                print("action_txType - Hex")        
                self.action_Tx_Hex.setChecked(True)
                self.action_Tx_Ascii.setChecked(False)
                self.txType_Set(TX_TYPE_HEX)

    #--------------------------------------------------
    #                       Timer
    #--------------------------------------------------
    def timer_UartRx(self):
        print_ascii = ""
        print_hex = ""
        now = ""

        if self.action_Rx_AttachCurrentTime.isChecked():
            now = datetime.now().strftime("%d/%m/%Y %H:%M:%S - ")

        while True:
            read_msg = self.comport_sel.read(READ_MSG_NUM)
            if len(read_msg) == 0:
                if len(print_ascii):
                    self.textEdit_ascii.append(now + print_ascii)
                if len(print_hex):
                    self.textEdit_hex.append(now + print_hex)
                return
                
            for read_byte in read_msg:
                if self.action_Text_Hex.isChecked():
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
    def comport_Set(self):
        comlist = serial.tools.list_ports.comports()
        connected = []
        for element in sorted(comlist):
            connected.append(element.device)
        self.comboBox_ComPort.addItems(connected)
        # if len(connected) == 1:
            # self.button_Connect()

    def comport_Read(self, str_action):
        if str_action == "Reading":
            self.pushButton_Stop.setText("Reading")
            self.pushButton_Stop.setStyleSheet(";background-color:rgb(204,239,220);font: 12pt 'Arial';")
            self.comport_sel.flushInput()
            self.comport_timer.start(200)
        else:
            self.pushButton_Stop.setText("Stopped")
            self.pushButton_Stop.setStyleSheet("background-color:rgb(255,204,204);font: 12pt 'Arial';")
            self.comport_timer.stop()

    def textEdit_Resize(self):
        # Get current MainForm size
        mainform_width = self.frameGeometry().width()
        mainform_height = self.frameGeometry().height()

        if self.action_Text_Hex.isChecked():
            self.textEdit_hex.setVisible(True)
            # Set textEdit_hex size
            textEdit_hex_width = (mainform_width - self.groupBox_Comport.frameGeometry().width() - 10 - 10 - 10 - 10) * 3 / 4
            textEdit_hex_height = (mainform_height - 30) - self.groupBox_Tx.frameGeometry().height() - 30 - 60
            self.textEdit_hex.resize(textEdit_hex_width, textEdit_hex_height)
            
            label_HexPos_width = textEdit_hex_width
            self.label_HexPos.resize(label_HexPos_width, self.label_HexPos.frameGeometry().height())
            
            # Set textEdit_ascii position and size
            textEdit_ascii_width = (mainform_width - self.groupBox_Comport.frameGeometry().width() - 10 - 10 - 10 - 10) * 1 / 4
            textEdit_ascii_height = (mainform_height - 30) - self.groupBox_Tx.frameGeometry().height() - 30 - 60
            textEdit_ascii_x = mainform_width - 10 - textEdit_ascii_width
            textEdit_ascii_y = self.textEdit_ascii.frameGeometry().y()
            self.textEdit_ascii.move(textEdit_ascii_x, textEdit_ascii_y)
            self.textEdit_ascii.resize(textEdit_ascii_width, textEdit_ascii_height)
            
        else:
            self.textEdit_hex.setVisible(False)
            # Set textEdit_ascii position and size
            textEdit_ascii_width = (mainform_width - self.groupBox_Comport.frameGeometry().width() - 10 - 10 - 10 - 10)
            textEdit_ascii_height = (mainform_height - 30) - self.groupBox_Tx.frameGeometry().height() - 30 - 60
            textEdit_ascii_x = self.textEdit_hex.frameGeometry().x()
            textEdit_ascii_y = self.textEdit_ascii.frameGeometry().y()
            self.textEdit_ascii.move(textEdit_ascii_x, textEdit_ascii_y)
            self.textEdit_ascii.resize(textEdit_ascii_width, textEdit_ascii_height)

    def txType_Set(self, tx_type):
        if tx_type == TX_TYPE_HEX:
            self.label_Tx_HexNum.setVisible(True)
            self.lineEdit_Tx.setInputMask(INPUT_MASK_HEX)
        else:
            self.label_Tx_HexNum.setVisible(False)
            self.lineEdit_Tx.setInputMask(INPUT_MASK_NONE)

###################################################
#                   Main function
###################################################
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())