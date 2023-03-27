from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from ui.form.message_form_ui import Ui_message_form

class MessageForm(QWidget, Ui_message_form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def set_font_size(self, font_size:int):
        font = self.listWidget_hotkey.font()
        font.setPointSize(font_size)
        self.listWidget_hotkey.setFont(font)

    def show(self) -> None:
        return super().show()

    def clear(self):
        self.listWidget_hotkey.clear()

    def addItem(self, item_string:str):
        self.listWidget_hotkey.addItem(item_string)