import sys
from PyQt5 import QtCore,QtGui,QtWidgets
from PyQt5.QtCore import QCoreApplication,Qt
from PyQt5.QtWidgets import QApplication , QMainWindow, QDialog,QMessageBox
from application.uipy.load import Ui_Dialog
import sqlite3
##from PyQt5 import QtSql
##from PyQt5.QtSql import QSqlQuery

##from mainfunction import main_function
##from facefunction import face_function


class load_function(Ui_Dialog,QDialog):
    def __init__(self,log,parent = None):
        super(load_function,self).__init__()
        self.setupUi(self)
        self.logger = log
        self.pushButton.clicked.connect(self.check)
        self.pushButton_2.clicked.connect(self.close)
        self.value = 0
        self.account = ""

    def check(self):
        if self.lineEdit.text() == "" or self.lineEdit_2.text() == "":
            self.showMessageBox_critical("Error","Please enter your username and password!")
        else:
            try:
                conn = sqlite3.connect('./face_register/register.db')
                c = conn.cursor()
                cursor = c.execute('SELECT password from admin where account = \"'+ self.lineEdit.text()+'\"')
                for row in cursor.fetchall():
                    if row[0] == self.lineEdit_2.text():
                        self.value = 1
                        self.account = self.lineEdit.text()
                        self.close()
                        break
                conn.close()
                self.logger.info('manager load!')
                                        
            except:
                self.showMessageBox_critical("Error","Unable to connect to database!")
                self.logger.error('\nUnable to connect to database!\n')
            if self.value == 0:
                self.showMessageBox_critical("Error","Incorrect username or password")

    
    def showMessageBox_critical(self, title, message):
        msgBox=QMessageBox()
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.setWindowTitle(title)
        msgBox.setText(message)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec_()
        del msgBox

'''if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = load_function()
    ui_main = main_function()
    window.show()
    sys.exit(app.exec_())'''