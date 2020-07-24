from PyQt5.QtGui import QFont
FONT_FAMILY = 'Microsoft YaHei'

class Font(QFont):
    def __init__(self, *__args):
        super().__init__(*__args)

        self.font_family = FONT_FAMILY
        self.point_size = 12

    @property
    def font_family(self) -> None:
        return None

    @font_family.setter
    def font_family(self, value: str = FONT_FAMILY) -> None:
        self.setFamily(value)

    @property
    def point_size(self):
        return self.pointSize()

    @point_size.setter
    def point_size(self, value: int = 12):
        if value < 0:
            value = 12
        self.setPointSize(value)
