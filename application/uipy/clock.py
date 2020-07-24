from math import sin, cos, radians
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtWidgets import QWidget
from .label import Label
CLOCK_MIN_SIZE = 300

class Clock(QWidget):
    def __init__(self, parent=None, *args):
        super().__init__(parent, *args)

        self._weekdays = ['Mon.', 'Tues.', 'Wed.', 'Thurs.', 'Fri.', 'Sat.', 'Sun.']
        self.clock_size = CLOCK_MIN_SIZE
        self.calendar_width = 160
        self.hour, self.minute, self.second = 0, 0, 0
        self.lbl_year_month = Label('', self, 20)
        self.lbl_year_month.setMinimumWidth(self.calendar_width)
        self.lbl_day = Label('', self, 50)
        self.lbl_day.setMinimumWidth(self.calendar_width)
        self.lbl_weekday = Label('', self, 18)
        self.lbl_weekday.setMinimumWidth(self.calendar_width)
        self.resize(self.clock_size)

    @property
    def date(self) -> None:
        return None

    @date.setter
    def date(self, value: [int]) -> None:
        self.lbl_year_month.setText('%d/%02d' % (value[0], value[1]))
        self.lbl_day.setText(str(value[2]))
        self.lbl_weekday.setText(self._weekdays[value[3]])

    @property
    def time(self) -> [int]:
        return [self.hour, self.minute, self.second]

    @time.setter
    def time(self, value: [int]) -> None:
        self.hour, self.minute, self.second = value
        self.update()

    def resize(self, size: int = CLOCK_MIN_SIZE):
        if size < CLOCK_MIN_SIZE:
            size = CLOCK_MIN_SIZE
        self.clock_size = size
        self.setMinimumWidth(size + self.calendar_width)
        self.setMinimumHeight(size)
        self.lbl_year_month.move(size, 10)
        self.lbl_day.setMinimumHeight(size)
        self.lbl_day.move(size, 0)
        self.lbl_weekday.move(size, size - 10 - self.lbl_weekday.height())
        super().resize(size + self.calendar_width, size)

    def paintEvent(self, *args):
        size = self.clock_size
        half = size / 2

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        pen = QPen()
        pen.setCapStyle(Qt.RoundCap)

        # 大刻度
        pen.setColor(Qt.black)
        pen.setWidth(5)
        painter.setPen(pen)
        for i in range(12):
            rad = radians(i * 30)
            x1 = half - (half - 5) * sin(rad)
            y1 = half - (half - 5) * cos(rad)
            x2 = half - (half - 20) * sin(rad)
            y2 = half - (half - 20) * cos(rad)
            painter.drawLine(x1, y1, x2, y2)

        # 表盘
        pen.setColor(Qt.darkBlue)
        pen.setWidth(9)
        painter.setPen(pen)
        painter.drawEllipse(5, 5, size - 10, size - 10)

        # 时针
        pen.setColor(Qt.black)
        pen.setWidth(13)
        painter.setPen(pen)
        rad = radians(self.hour * 30 + self.minute / 2)
        x1 = half + half * 0.55 * sin(rad)
        y1 = half - half * 0.55 * cos(rad)
        x2 = half - 15 * sin(rad)
        y2 = half + 15 * cos(rad)
        painter.drawLine(x1, y1, x2, y2)

        # 分针
        pen.setWidth(8)
        painter.setPen(pen)
        rad = radians(self.minute * 6 + self.second / 10)
        x1 = half + half * 0.7 * sin(rad)
        y1 = half - half * 0.7 * cos(rad)
        x2 = half - 15 * sin(rad)
        y2 = half + 15 * cos(rad)
        painter.drawLine(x1, y1, x2, y2)

        # 秒针
        pen.setColor(Qt.darkRed)
        pen.setWidth(5)
        painter.setPen(pen)
        rad = radians(self.second * 6)
        x1 = half + half * 0.85 * sin(rad)
        y1 = half - half * 0.85 * cos(rad)
        x2 = half - 20 * sin(rad)
        y2 = half + 20 * cos(rad)
        painter.drawLine(x1, y1, x2, y2)

        # 小圆圈
        pen.setWidth(1)
        painter.setPen(pen)
        painter.setBrush(Qt.darkRed)
        painter.drawEllipse(half - 9, half - 9, 18, 18)
