from __future__ import unicode_literals
# 解决2.x到3.x的字符串问题
from os.path import dirname, abspath
import sys

from PyQt5.QtCore import QSize, QEasingCurve
from PyQt5.QtWidgets import QApplication, QMainWindow, QScrollArea, QWidget, \
    QGridLayout, QLabel, QVBoxLayout

from application.uipy.uilib.widgets.MetroProgress import MetroProgressBar

class TestMetroProgressBar(QMainWindow):

    def __init__(self, parent = None):
        super(TestMetroProgressBar, self).__init__(parent)
        self.setObjectName("Test_MetroProgressCircleBar")
        self.resize(QSize(400, 100))
        self.mpbs = []    # 所有的进度条
        self.initView()
        self.setStyleSheet("QScrollArea,QWidget{background-color: rgb(255, 255, 255);}")

    def closeEvent(self, event):
        for mpb in self.mpbs:    # @UnusedVariable
            mpb.stop()    # 调用停止动画
        super(TestMetroProgressBar, self).closeEvent(event)

    def initView(self):
        '''创建界面'''
        scrollArea = QScrollArea(self)    # 滚动区域
        scrollArea.setWidgetResizable(True)
        self.setCentralWidget(scrollArea)

        scrollWidget = QWidget()
        scrollArea.setWidget(scrollWidget)
        gridLayout = QGridLayout(scrollWidget)    # 网格布局
        

        # 从QEasingCurve获取所有的type
        curve_types = [(n, c) for n, c in QEasingCurve.__dict__.items()
            if isinstance(c, QEasingCurve.Type)]
        curve_types.sort(key = lambda ct: ct[1])
        i = 0
        curve_name = curve_types[0][0]
        curve_type = curve_types[0][1]
        index = curve_type % 4
        widget = QWidget()
        widget.setObjectName("_BorderWidget")
        ##widget.setStyleSheet("QWidget#_BorderWidget{border: 1px solid black;}")
        name = QLabel("QEasingCurve." + curve_name, widget)
        mpb = MetroProgressBar(widget, curve_type)
        layout = QVBoxLayout(widget)
        layout.addWidget(name)
        layout.addWidget(mpb)
        gridLayout.addWidget(widget, i, index, 1, 1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestMetroProgressBar()
    window.show()
    sys.exit(app.exec_())