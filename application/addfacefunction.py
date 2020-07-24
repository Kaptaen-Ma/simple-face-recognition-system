from __future__ import print_function
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QCoreApplication, QTimer
from PyQt5.QtWidgets import QMessageBox,QWidget,QDialog,QFileDialog
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QThread
import cv2
import argparse
from application.detect import *
import numpy
import os
import qimage2ndarray
import shutil
import sys
from application.uipy.camera import Ui_Dialog

class addface_function(Ui_Dialog,QDialog):
    def __init__(self,cap,cascade,parent = None):
        super(addface_function,self).__init__()
        self.setupUi(self)
        self.photo_num = 0
        self.thread = Worker(cap)
        self.thread.sinOut.connect(self.get_frame)
        self.pushButton.clicked.connect(self.quit)
        self.face_cascade = cascade
        self.thread.start()
        self.photo_timer = QTimer()
        self.photo_timer.setInterval(100)
        self.photo_timer.timeout.connect(self.photo)
        self.photo_flag = False
        self.label.setText('shooting process ...... ')
        self.showMessageBox_info('Info','Please keep your face facing the camera!')
        self.photo_flag = True
        self.photo_timer.start()

    def quit(self):
        self.thread.__del__()
        self.close()
    
    def photo(self):
        if self.photo_flag and self.photo_num < 15:
            process = str(int(self.photo_num/15*100))+'%'
            self.label_2.setText('shooting process ...... '+process)
            a = QPixmap.toImage(self.label.pixmap())
            frame = qimage2ndarray.rgb_view(a)  
            frame = cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)
            faces = detectAndDisplay(frame, self.face_cascade)
            if len(faces) == 1:
                self.photo_num += 1
                ##self.logger.info('shoot the person(studentid number:'+self.comboBox_2.currentText()+'the '+str(self.photo_num)+' photo)')
                frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                faceROI = frame[faces[0][1]:(faces[0][1] + faces[0][3]),faces[0][0]:(faces[0][0]+faces[0][2])]
                myface = cv2.resize(faceROI,(92,111),0,0,cv2.INTER_AREA)
                cv2.imwrite('./temp/'+str(self.photo_num)+'.pgm',myface)
            elif len(faces) == 0:
                self.label_2.setText('No face detected,Please move to a brightly lit place!')
            elif len(faces)>1:
                self.label_2.setText('Please keep only one face in front of the camera!')
                
        elif self.photo_flag and self.photo_num == 15:
            self.photo_timer.stop()
            self.label_2.setText('shooting process ...... 100%')
            self.showMessageBox_info('Info','Photo finished')
            self.quit()

    
    def showMessageBox(self, title, message):
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
        msgBox.button(QMessageBox.Ok).animateClick(3000)
        msgBox.exec_()
        del msgBox

    def get_frame(self,frame,rt):

        if rt == 0:
            self.showMessageBox("Error","Unable to read camera's data stream!")
            ##self.logger.error('\nUnable to read camera\'s data stream! Please check and restart it!\n')
            self.close()
        elif rt == 1:
            self.label.setPixmap(QPixmap.fromImage(frame))
        elif rt == -1:
            self.showMessageBox("Error","Unable to open camera, please check and restart device!")
            ##self.logger.error('\nUnable to open camera, please check and restart device!\n')
            self.close()
        elif rt == -2:
            self.showMessageBox("Error","Unable to load face data set")
            ##self.logger.error('\nUnable to load face data set\n')
            self.close()

class Worker(QThread):
    sinOut = QtCore.pyqtSignal(object,int)

    def __init__(self,cap,parent=None):
        super(Worker, self).__init__(parent)
        self.working = True
        self.cap = cap
  

    def __del__(self):
        self.working = False
        self.quit()
        self.wait()

    def run(self):
        rt = -1 

        if not self.cap.isOpened():
            a = -1
            self.working == False
            self.sinOut.emit(a,rt)
        rt = 1
        while self.working == True:
            ret,frame = self.cap.read()

            if not ret:
                rt = 0
                a = -1
                self.working == False
            
            frame = cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)
            a = QImage(frame.data,frame.shape[1],frame.shape[0],QImage.Format_RGB888)

            self.sinOut.emit(a,rt)
            
            if self.working == False:
                break