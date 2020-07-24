import sys
from PyQt5 import QtCore,QtGui,QtWidgets
from PyQt5.QtCore import QCoreApplication,Qt,QThread,QObject,pyqtSignal
from PyQt5.QtWidgets import QApplication , QMainWindow, QDialog,QMessageBox
from PyQt5.QtGui import QImage, QPixmap
from application.uipy.recog import Ui_Dialog
from application.detect import *
import cv2
'''from gpiozero import LED'''
from time import sleep
import sqlite3
import numpy
from config import DETECT_PERIOD,RECOG_FRAME,DETECT_FACTOR, MISS_TIME

class recog_function(Ui_Dialog,QDialog):
    def __init__(self,cap,log,recog_log,detect_model,recog_model,parent = None):
        super(recog_function, self).__init__()
        self.setupUi(self)
        self.logger = log
        self.re_logger = recog_log
        self.reg = True
        if detect_model == []:
            self.showMessageBox("Error","Unable to load face detect data set!")
            self.logger.error('\nUnable to load face detect data set!\n')
            self.exit()
        if recog_model == []:
            self.showMessageBox("Error","Unable to load face recog data set!")
            self.logger.error('\nUnable to load face recog data set!\n')
            self.exit()
        self.recog_model=recog_model
        self.thread = Worker(cap,detect_model)
        ##self.thread2 = QThread()
        self.thread.sinOut.connect(self.get_frame)
        self.thread.start()
        self.pushButton.clicked.connect(self.exit)
        
    
    def exit(self):
        self.thread.__del__()
        self.reg = False
        self.re_logger.info('Face-recignition ended!')
        ##self.thread.quit()
        self.close()
    
    def hide(self):
        self.thread.__del__()
        self.close()

    def showMessageBox(self, title, message):
        msgBox=QMessageBox()
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.setWindowTitle(title)
        msgBox.setText(message)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.button(QMessageBox.Ok).animateClick(3000)  
        msgBox.exec_()
        del msgBox
    
    def opendoor(self):
        print(1)
        '''door = LED(17)
        door.on()
        sleep(1)
        door.off()'''
    
    def show(self,lab):
        try:
            conn = sqlite3.connect('./face_register/register.db')
            c = conn.cursor()
            cursor = c.execute('SELECT name, matrikelnummer from face where label = '+str(lab-40)+'')
            for row in cursor.fetchall():
                self.label_2.setText('matrikelnummer:'+row[1]+'--name:'+row[0])
                self.re_logger.info('matrikelnummer:'+row[1]+'--name:'+row[0]+'have been recognized!')
            conn.close()
        except:
            self.logger.error('\nUnable to connect to database!\n')
            self.showMessageBox('Error','Unable to connect to database!')
    
    def get_frame(self,frame,rt,face):

        if rt == 0:
            self.showMessageBox("Error","Unable to read camera\'s data stream!")
            self.logger.error('\nUnable to read camera\'s data stream! Please check and restart it!\n')
            self.close()
        elif rt == 1:
            frame = cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)
            a = QImage(frame.data,frame.shape[1],frame.shape[0],QImage.Format_RGB888)
            self.label.setPixmap(QPixmap.fromImage(a))
        elif rt == -1:
            self.showMessageBox("Error","Unable to open camera, please check and restart device!")
            self.logger.error('\nUnable to open camera, please check and restart device!\n')
            self.exit()
        elif rt == 2:
            frame = cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)
            a = QImage(frame.data,frame.shape[1],frame.shape[0],QImage.Format_RGB888)
            self.label.setPixmap(QPixmap.fromImage(a))
        elif rt == -2:
            self.showMessageBox("Error","Unable to load face data set!")
            self.logger.error('\nUnable to load face data set!\n')
        elif rt == 3:
            self.re_logger.error('\nnot enough face-matching\n')
            self.label_2.setText('not enough face-matching')
        elif rt == -3:
            self.label_2.setText("load face_dataset...")
        elif rt == 4:
            frame = cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)
            a = QImage(frame.data,frame.shape[1],frame.shape[0],QImage.Format_RGB888)
            self.label.setPixmap(QPixmap.fromImage(a))
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faceROI = frame_gray[face[1]:(face[1] + face[3]),face[0]:(face[0]+face[2])]
            faceROI = cv2.resize(faceROI,(92,112),0,0,cv2.INTER_AREA)
            #直接主线程做了
            lab,confidence = self.recog_model.predict(faceROI)
            if lab>40:
                try:
                    conn = sqlite3.connect('./face_register/register.db')
                    c = conn.cursor()
                    cursor = c.execute('SELECT name, matrikelnummer from face where label = '+str(lab-40)+'')
                    for row in cursor.fetchall():
                        self.label_2.setText('matrikelnummer:'+row[1]+'--name:'+row[0])
                        self.re_logger.info('matrikelnummer:'+row[1]+'--name:'+row[0]+' have been recognized!')
                    conn.close()
                except:
                    self.logger.error('\nUnable to connect to database!\n')
                    self.re_logger.error('Unable to connect to database!')
                    self.showMessageBox('Error','Unable to connect to database!')
            else:
                self.label_2.setText('--Unknow')
                self.re_logger.warning('--Unknow')
        elif rt == -4:
            self.hide()
        elif rt == 5:
            frame = cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)
            a = QImage(frame.data,frame.shape[1],frame.shape[0],QImage.Format_RGB888)
            self.label.setPixmap(QPixmap.fromImage(a))
            self.label_2.setText('detect...')

''' 
    根据线程的返回值判断状态
    rt = 0:
        无法读取相机的数据流
    rt = 1：
        正常读取相机的数据流并进行显示，但不进行人脸的识别
    rt = -1:
        无法打开摄像头
    rt = 2:
        正常读取相机的数据流并进行显示，但不进行人脸的识别和检测
    rt = -2:
        无法加载人脸检测数据集
    rt = 3:
        人脸识别的匹配度不够
    rt = -3:
        正在加载人脸数据集
    rt = 4:
        正常读取相机的数据流并进行显示，识别到了人脸，根据label读数据库进行显示
    rt = -4:
        界面隐藏但不关闭
    rt = 5:
        未检测到人脸
'''
class Worker(QThread):
    sinOut = QtCore.pyqtSignal(object,int,list)
    
    def __init__(self,cap,detect_model,parent=None):
        super(Worker, self).__init__(parent)
        #设置工作状态与初始num数值
        self.working = True
        self.num = 0
        self.cap = cap
        self.ALL_P = DETECT_PERIOD
        self.DETECT_P = RECOG_FRAME
        self.Ms_time = 0
        if detect_model == []:
            self.working = False
        else:
            self.detect_model =detect_model


    def __del__(self):
        #线程状态改变与线程终止
        self.working = False
        self.quit()
        self.wait()

    def run(self):
        a=-1
        rt = -2 #返回值
        face = []
        ## 相机操作
        if not self.cap.isOpened():
            a = -1
            rt = -1
            self.sinOut.emit(a,rt,face)
            self.working = False

        while self.working == True:
            rt = 1
            ret,frame = self.cap.read()
            face = []
            if not ret:
                rt = 0
                a = -1
                self.working = False
            
            if self.num >= int(self.ALL_P*DETECT_FACTOR) and self.num <self.ALL_P:
                faces = detectAndDisplay(frame, self.detect_model)
                if len(faces) >=1:
                    cv2.rectangle(frame,(faces[0][0],faces[0][1]),(faces[0][0]+faces[0][2],faces[0][1]+faces[0][3]),(255, 0, 255),4)
                    if self.num >=self.ALL_P-self.DETECT_P:
                        rt =4
                        for num in range(4):
                            face.append(faces[0][num])
                    self.sinOut.emit(frame,rt,face)
                else:
                    self.Ms_time +=1
                self.num +=1
            else:
                if self.num == int(self.ALL_P/3*2):
                    rt = 5
                    self.sinOut.emit(frame,rt,face)
                if self.num < self.ALL_P:
                    self.num += 1
                else:
                    rt = 2
                    self.num = 0
                self.sinOut.emit(frame,rt,face)
            
            if self.Ms_time == MISS_TIME:
                rt = -4
                self.sinOut.emit(frame,rt,face)
            
            if self.working == False:
                break
