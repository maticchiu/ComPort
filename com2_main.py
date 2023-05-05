from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import datetime
import time
from enum import Enum
import os

import ui.form.com2_window_ui as ui
from ui.comport_setting import Uart
from ui.message_form import MessageForm

# import ctypes
# myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
# ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

class Console(Enum):
    INDEX_0 = 0x01
    INDEX_1 = 0x02
    INDEX_ALL = INDEX_0 or INDEX_1

class ComportRx(QMainWindow, ui.Ui_ComPortWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setWindowIcon(QIcon('./res/icon.png'))

        self.setStyleSheet("background-color:rgb(0,0,0);")
        self.font().setFamily('Courier New')
        self.font().setPointSize(10)
        self.statusbar.setStyleSheet("color:rgb(128,255,128)")

        self.font_size = 10

        self.uart_num = 2
        self.current_console:Console = Console.INDEX_ALL
        self.timestamp_enable = True
        self.read_uart_message = True

        self.textEdit_com0 = QTextEdit(self)
        self.textEdit_com1 = QTextEdit(self)

        self.uarts = Uart()

        self.uarts.signal_update_uart.connect(self.signal_update_uart_status)

        self.timer_com0 = QTimer(self)
        self.timer_com1 = QTimer(self)

        self.timer_com0.timeout.connect(self.timer_Rx_Com0)
        self.timer_com1.timeout.connect(self.timer_Rx_Com1)

        self.message_form = MessageForm()


    def start(self):
        def initTextEdit(textedit:QTextEdit):
            textedit.setReadOnly(True)
            textedit.textChanged.connect(self.textedit_TextChanged)
            textedit.setStyleSheet("color:rgb(0,170,0)")
            textedit.setFontFamily('Courier New')
            textedit.setFontPointSize(self.font_size)

        initTextEdit(self.textEdit_com0)
        initTextEdit(self.textEdit_com1)

        self.uarts.autoConnect()
        self.textedit_Resize()
        self.updateWindowTitle()

        self.timer_com0.start(100)
        self.timer_com1.start(100)

    #
    #           Window Event
    #
    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.textedit_Resize()
        return super().resizeEvent(a0)

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.message_form.close()
        self.uarts.close()
        return super().closeEvent(a0)

    #
    #           Connection
    #
    def textedit_TextChanged(self):
        self.textEdit_com0.verticalScrollBar().setValue(self.textEdit_com0.verticalScrollBar().maximum())
        self.textEdit_com1.verticalScrollBar().setValue(self.textEdit_com1.verticalScrollBar().maximum())

    def timer_Rx_Com0(self):
        if self.read_uart_message:
            self.receive_msg(self.textEdit_com0, self.uarts.readComport0)

    def timer_Rx_Com1(self):
        if self.read_uart_message:
            self.receive_msg(self.textEdit_com1, self.uarts.readComport1)

    def signal_update_uart_status(self):
        self.updateWindowTitle()

    #
    #           Hotkey
    #
    def keyPressEvent(self, key_event: QKeyEvent) -> None:
        if key_event.modifiers() & Qt.ControlModifier:
            self.runCtrlKeyEvent(key_event.key())
        else:
            self.runSingleKeyEvent(key_event.key())

        return super().keyPressEvent(key_event)
    
    def runSingleKeyEvent(self, pressed_key):
        print(f"Single key = ({hex(pressed_key)})")
        match pressed_key:
            case Qt.Key.Key_F1:     # Show message form
                self.showHotKeyList()
            case Qt.Key.Key_F2:
                self.uarts.show()
            case Qt.Key.Key_1:
                self.setConsoleIndex(Console.INDEX_0)
            case Qt.Key.Key_2:
                self.setConsoleIndex(Console.INDEX_1)
            case Qt.Key.Key_3:
                self.setConsoleIndex(Console.INDEX_ALL)
            case Qt.Key.Key_C:
                if self.current_console == Console.INDEX_0 or self.current_console == Console.INDEX_ALL or self.uart_num == 1:
                    self.textEdit_com0.clear()
                    self.uarts.flushComport0()
                if self.uart_num == 2 and (self.current_console == Console.INDEX_1 or self.current_console == Console.INDEX_ALL):
                    self.textEdit_com1.clear()
                    self.uarts.flushComport1()
                self.statusbar.showMessage("Clear message")
            case Qt.Key.Key_T:
                self.timestamp_enable = not self.timestamp_enable

    def runCtrlKeyEvent(self, pressed_key):
        def setFontSize(textedit:QTextEdit, font_size:int):
            cursor_rx = textedit.textCursor()
            textedit.selectAll()
            textedit.setFontPointSize(font_size)
            textedit.setTextCursor(cursor_rx)
            textedit.setFontPointSize(font_size)

        print(f"ctrl key = ({hex(pressed_key)})")
        match pressed_key:
            case Qt.Key.Key_PageUp:
                if self.font_size < 24:
                    self.font_size += 2
                if self.current_console == Console.INDEX_0 or self.current_console == Console.INDEX_ALL:
                    setFontSize(self.textEdit_com0, self.font_size)
                if self.current_console == Console.INDEX_1 or self.current_console == Console.INDEX_ALL:
                    setFontSize(self.textEdit_com1, self.font_size)
                self.statusbar.showMessage(f"Font size = {self.font_size}")
            case Qt.Key.Key_PageDown:
                if self.font_size > 8:
                    self.font_size -= 2
                if self.current_console == Console.INDEX_0 or self.current_console == Console.INDEX_ALL:
                    setFontSize(self.textEdit_com0, self.font_size)
                if self.current_console == Console.INDEX_1 or self.current_console == Console.INDEX_ALL:
                    setFontSize(self.textEdit_com1, self.font_size)
                self.statusbar.showMessage(f"Font size = {self.font_size}")
            case Qt.Key.Key_S:
                if self.uart_num == 1:
                    self.statusbar.showMessage("No switch. Only 1 com port.")
                elif self.uart_num == 2:
                    self.uarts.switchComports()
                    self.statusbar.showMessage("Switch com ports")
                self.updateWindowTitle()
            case Qt.Key.Key_R:
                self.uarts.flushComport0()
                self.uarts.flushComport1()
                self.read_uart_message = not self.read_uart_message
                if self.read_uart_message:
                    self.statusbar.showMessage("Start reading uart")
                else:
                    self.statusbar.showMessage("Stop reading uart")
            case Qt.Key.Key_L:
                if self.uarts.getName_Com0() != "":
                    self.saveLog(self.uarts.getName_Com0(), self.textEdit_com0.toPlainText())
                if self.uarts.getName_Com1() != "" and self.uart_num == 2:
                    self.saveLog(self.uarts.getName_Com1(), self.textEdit_com0.toPlainText())
                path = os.path.realpath("./log")
                os.startfile(path)
                self.statusbar.showMessage("Save log to ./log")
            case Qt.Key.Key_A:
                self.uarts.autoConnect()
                self.updateWindowTitle()
            case Qt.Key.Key_1:
                self.uart_num = 1
                self.uarts.close_Com1()
                self.textedit_Resize()
            case Qt.Key.Key_2:
                self.uart_num = 2
                self.uarts.autoConnect()
                self.textedit_Resize()
            case Qt.Key.Key_T:
                if self.windowFlags() & Qt.WindowStaysOnTopHint:
                    self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinMaxButtonsHint)
                    print("Windows normally")
                else:
                    self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinMaxButtonsHint | Qt.WindowStaysOnTopHint)
                    print("Windows stay on top")
                self.setVisible(True)

    #
    #           Function
    #
    def updateWindowTitle(self):
        if self.uart_num == 2:
            self.setWindowTitle(f"{self.uarts.getName_Com0()} - {self.uarts.getName_Com1()}")
        else:
            self.setWindowTitle(f"{self.uarts.getName_Com0()}")

    def textedit_Resize(self):
        if self.uart_num == 2:
            self.textEdit_com0.move(0, 0)
            self.textEdit_com0.resize(int(self.width()/2 - 5), self.height() - 20)
            self.textEdit_com1.setVisible(True)
            self.textEdit_com1.setGeometry(self.textEdit_com0.rect())
            self.textEdit_com1.move(self.textEdit_com0.rect().topRight() + QPoint(10, 0))
        else:
            self.textEdit_com1.setVisible(False)
            self.textEdit_com0.resize(self.size() - QSize(0, 20))
        self.updateWindowTitle()

    def setConsoleIndex(self, idx: Console):
        self.current_console = idx
        print(f"Console index = {self.current_console}")

    def receive_msg(self, textedit:QTextEdit, read_func):
        msg_queue = ""
        while True:
            time.sleep(0.05)
            rx_msg:str = read_func().decode("utf-8").replace("\r", "")
            if len(rx_msg) == 0:
                if len(msg_queue) > 0:
                    textedit.append(msg_queue)
                    msg_queue = ""
                return
            
            msg_queue += rx_msg

            if "\n" in msg_queue:
                msg_list = msg_queue.split("\n")
                for msg_item in msg_list[:-1]:
                    now = ""
                    if self.timestamp_enable:
                        now = datetime.datetime.now().strftime(f"[%H:%M:%S.{'%03d' % (datetime.datetime.now().microsecond / 1e3)}] ")
                    textedit.append(now + msg_item)
                msg_queue = msg_list[-1]

    def saveLog(self, com_name:str, log_content:str):
        def mkdir(folder_name):
            if os.path.isdir(folder_name):
                print(f"Folder exists: {folder_name}")
                return
            print("Create folder: " + folder_name)
            os.makedirs(folder_name)

        mkdir("./log")
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_name = f"./log/log_{now}_{com_name.lower()}.log"
        f = open(log_name, "w+")
        f.write(log_content)
        f.close()

    #
    # Message Form
    #
    def showHotKeyList(self):
        self.message_form.clear()
        self.message_form.set_font_size(9)
        self.message_form.addItem("------------ Single Key List ------------")
        self.message_form.addItem("  F1:    Show message form")
        self.message_form.addItem("  F2:    Com port setting")
        self.message_form.addItem("")
        self.message_form.addItem("  1:     Set Console 1")
        self.message_form.addItem("  2:     Set Console 2")
        self.message_form.addItem("  3:     Set Console 1 & 2")
        self.message_form.addItem("  C:     Clear console")
        self.message_form.addItem("  T:     Toggle timestamp")
        self.message_form.addItem("")
        self.message_form.addItem("------------ Ctrl Key List ------------")
        self.message_form.addItem("  1:     Show 1 console")
        self.message_form.addItem("  2:     Show 2 consoles")
        self.message_form.addItem("  S:     Switch console")
        self.message_form.addItem("  R:     Read / Stop uart message")
        self.message_form.addItem("  L:     Save log")
        self.message_form.addItem("  A:     Auto connection")
        self.message_form.addItem("  T:     Toggle 'Windows stay on top'")
        self.message_form.show()



###################################################
#                   Main function
###################################################
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = ComportRx()
    window.show()
    window.start()
    sys.exit(app.exec_())
