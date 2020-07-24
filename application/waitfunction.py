from application.uipy.wait import Ui_Dialog
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QCoreApplication, QTimer,Qt
from PyQt5.QtWidgets import QMessageBox,QWidget,QDialog
from PyQt5.QtWidgets import QApplication,QMainWindow,QDialog,QVBoxLayout
from application.uipy.MetroCircleProgress import MetroCircleProgress
import sys


class wait_function(Ui_Dialog, QDialog):
    def __init__(self,parent=None):
        super(wait_function, self).__init__()
        self.setupUi(self)
        self.verticalLayout.addWidget(MetroCircleProgress(self,styleSheet="""
            qproperty-color: rgb(0, 0, 255);
        """))

