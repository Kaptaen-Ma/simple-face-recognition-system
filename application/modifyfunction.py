import sys
from PyQt5 import QtCore,QtGui,QtWidgets
from PyQt5.QtCore import QCoreApplication,Qt
from PyQt5.QtWidgets import QApplication , QMainWindow, QDialog,QMessageBox
from application.uipy.usermodify import Ui_Dialog
import sqlite3

class modify_function(Ui_Dialog,QDialog):
    def __init__(self,account,log,parent = None):
        super(modify_function,self).__init__()
        self.setupUi(self)
        self.logger = log
        self.lineEdit.setText(account)
        self.pushButton.clicked.connect(self.check)
        self.pushButton_2.clicked.connect(self.close) 

    def check(self):
        if self.lineEdit.text() == "" or self.lineEdit_2.text() == "" or self.lineEdit_3.text() == "":
            self.showMessageBox_critical("Error","Please enter your username and password!")
        elif self.lineEdit_2.text() != self.lineEdit_3.text():
            self.showMessageBox_critical("Error","Inconsistent with the confirmed password!")
        else:
            try:
                conn = sqlite3.connect('./face_register/register.db')
                c = conn.cursor()
                cursor = c.execute('UPDATE admin SET account = \"'+ self.lineEdit.text()+'\",password = \"'+ self.lineEdit_2.text()+'\" where id = 1')
                conn.commit()
                conn.close()
                self.showMessageBox_info('Info','Successfully modified!')
                self.logger.info('Modify account successfully!')
                self.close()
            except:
                self.showMessageBox_critical("Error","Unable to connect to database")
                self.logger.error('\nUnable to connect to database!\n')

    def showMessageBox_critical(self, title, message):
        msgBox=QMessageBox()
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.setWindowTitle(title)
        msgBox.setText(message)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec_()
        del msgBox
    
    def showMessageBox_info(self, title, message):
        msgBox=QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setWindowTitle(title)
        msgBox.setText(message)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec_()
        del msgBox