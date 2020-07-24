from .font import Font
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel


class Label(QLabel):

    def __init__(self, text: str = '', parent=None, font_size: int = 12):
        super().__init__(text, parent)

        self._font = Font()
        self._font.point_size = font_size
        self.setFont(self._font)

        self.setAlignment(Qt.AlignCenter)
        self.setScaledContents(True)
        self.setText(text)
        self.setWordWrap(True)
        self.adjustSize()
