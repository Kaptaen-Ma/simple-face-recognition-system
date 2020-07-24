from PyQt5.QtWidgets import QPushButton

from .font import Font


class PushButton(QPushButton):
    def __init__(self, text='', parent=None):
        super().__init__(text, parent)

        self.setFont(Font())
