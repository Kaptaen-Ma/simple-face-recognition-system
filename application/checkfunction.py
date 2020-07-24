from application.uipy.check_photo import Ui_Dialog
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QCoreApplication, QTimer
from PyQt5.QtWidgets import QMessageBox,QWidget,QDialog
from PyQt5.QtGui import QImage, QPixmap
import cv2

class check_function(Ui_Dialog, QDialog):
    def __init__(self,photo,info,parent=None):
        super(check_function, self).__init__()
        self.setupUi(self)
        frame = cv2.cvtColor(photo,cv2.COLOR_RGB2BGR)
        a = QImage(frame.data,frame.shape[1],frame.shape[0],QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(a))
        self.label_2.setText('std nr:'+info[1]+' name:'+info[0])

