import sys
from PyQt5 import QtCore,QtGui,QtWidgets
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication , QMainWindow,QDialog
import os
from application.uipy.manage import Ui_Dialog
from application.deletefunction import delete_function
from application.facefunction import face_function
from application.loadfunction import load_function
from application.modifyfunction import modify_function

class manage_function(Ui_Dialog,QDialog):
	def __init__(self,cap, log, parent = None):
		super(manage_function, self).__init__()
		self.setupUi(self)
		self.logger = log
		self.log_read()
		self.pushButton.clicked.connect(self.log_read)
		self.pushButton_2.clicked.connect(self.face_photo)
		self.pushButton_3.clicked.connect(self.face_delete)
		self.pushButton_4.clicked.connect(self.close)
		self.pushButton_5.clicked.connect(self.modify_account)
		self.cap = cap

	def log_read(self):
		f = open('./recoglog.log','r',encoding='utf-8')
		self.plainTextEdit.setPlainText(f.read())
		f.close()
	
	def face_photo(self):
		'''try:
			
		except:
			self.showMessageBox_critical('Error','Camera Error!')'''
		face =face_function(self.cap,self.logger)
		face.setWindowModality(Qt.ApplicationModal)
		face.exec_()
		del face
	def face_delete(self):
		delete = delete_function(self.logger)
		delete.setWindowModality(Qt.ApplicationModal)
		delete.exec_()
		del delete
	
	def modify_account(self):
		load = load_function(self.logger)
		load.exec_()
		if load.value == 0:
			del load
			self.logger.warning('quit to load account_modify-site!')
		else:
			mo = modify_function(load.account,self.logger)
			del load
			self.logger.info('load in account_modify-site!')
			mo.setWindowModality(Qt.ApplicationModal)
			mo.exec_()
			del mo
	def showMessageBox_critical(self, title, message):
		msgBox=QMessageBox()
		msgBox.setIcon(QMessageBox.Critical)
		msgBox.setWindowTitle(title)
		msgBox.setText(message)
		msgBox.setStandardButtons(QMessageBox.Ok)
		msgBox.exec_()
		del msgBox