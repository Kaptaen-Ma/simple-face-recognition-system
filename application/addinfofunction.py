import sys
from PyQt5 import QtCore,QtGui,QtWidgets
from PyQt5.QtCore import QCoreApplication,Qt
from PyQt5.QtWidgets import QApplication , QMainWindow, QDialog,QMessageBox
from application.uipy.addinfo import Ui_Dialog
import sqlite3

class addinfo_function(Ui_Dialog,QDialog):
    def __init__(self,parent = None):
        super(addinfo_function,self).__init__()
        self.setupUi(self)
        self.get_stdinfo()
        self.buttonBox.accepted.connect(self.Check)
        self.comboBox.currentIndexChanged.connect(self.after_change_name)
        self.comboBox_2.currentIndexChanged.connect(self.after_change_stdnr)

    def after_change_name(self):
        self.comboBox_2.setCurrentText(self.comboBox_2.itemText(self.comboBox.currentIndex()))

    def after_change_stdnr(self):
        self.comboBox.setCurrentText(self.comboBox.itemText(self.comboBox_2.currentIndex()))
    
    def get_stdinfo(self):
        try:
            conn = sqlite3.connect('./face_register/register.db')
        
            conn.text_factory=str
            c = conn.cursor()

            cursor = c.execute('SELECT name, std_nr, class from add_info')
            for row in cursor.fetchall():
                self.comboBox.addItem(row[0])
                self.comboBox_2.addItem(row[1])
            conn.close()
        except:
            self.showMessageBox("Error","Unable to connect to database!")
            ##self.logger.error('\nUnable to connect to database!\n')
    
    def Check(self):
        if self.comboBox.currentText() == "" or self.comboBox_2.currentText() == "":
            self.showMessageBox("Error","Please enter your name and student number first!")
        else:
            self.accept()

    
    def showMessageBox(self, title, message):
        msgBox=QMessageBox()
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.setWindowTitle(title)
        msgBox.setText(message)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec_()
        del msgBox