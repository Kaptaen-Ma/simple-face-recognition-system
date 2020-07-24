##要分系统日志和识别日志
##要将识别界面放在钟的上方
##实现导入excel的功能
##将拍摄照片的进度编程进度条
import sys
from PyQt5 import QtCore,QtGui,QtWidgets
from PyQt5.QtCore import Qt, QCoreApplication,QTimer,QDateTime,QThread
from PyQt5.QtGui import *
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication,QMainWindow,QDialog,QVBoxLayout
import datetime
import os
import cv2
import sqlite3
import logging
from logging.handlers import TimedRotatingFileHandler
import requests
import re
from application.uipy.main import Ui_MainWindow
from application.managefunction import manage_function
from application.loadfunction import load_function
from application.recogfunction import recog_function
from application.uipy.clock import Clock
from application.uipy.label import Label
from application.detect import *
from config import AUTO_DETECT

class main_function(Ui_MainWindow,QMainWindow):
    def __init__(self, parent = None):
        super(main_function, self).__init__()
        self.setupUi(self)
        self.recogn = False
        self.models = []
        self.init = True
        init_thread = Update_Worker()
        init_thread.up.connect(self.model_update)
        init_thread.start()
        self.pushButton.clicked.connect(self.reco)
        self.pushButton_2.clicked.connect(self.manage)
        self.pushButton_3.clicked.connect(self.fresh_weather)
        ## 系统日志格式
        handler = TimedRotatingFileHandler("./facelog.log",when='D',interval=30,backupCount=2,encoding='utf-8')
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s |%(filename)s| %(levelname)s:%(message)s',datefmt='%Y-%m-%d %I:%M:%S %p')
        handler.setFormatter(formatter)
        ## 系统日志
        self.sys_logger = logging.getLogger('face_log')
        self.sys_logger.setLevel(level = logging.INFO)
        self.sys_logger.addHandler(handler)
        self.sys_logger.info('Application beginn to work...')
        ## 识别日志格式
        handler_re = TimedRotatingFileHandler("./recoglog.log",when='MIDNIGHT',interval=1,backupCount=30,encoding='utf-8')
        handler_re.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s | %(levelname)s:%(message)s',datefmt='%Y-%m-%d %I:%M:%S %p')
        handler_re.setFormatter(formatter)
        ## 识别日志
        self.recog_logger = logging.getLogger('recog_log')
        self.recog_logger.setLevel(level = logging.INFO)
        self.recog_logger.addHandler(handler_re)
        
        self.cap = cv2.VideoCapture()
        self.cap.open(0)
        if not self.cap.isOpened():
            self.showMessageBox_critical("Error","Unable to open camera, please check and restart device")
            self.sys_logger.error('\nUnable to open camera, please check and restart device\n')
        else:
            self.sys_logger.info('successfully open camera!')
        
        self.clock = Clock()
        self.clock.resize(400)

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.start()
        self.timer.timeout.connect(self.fresh_time)
        self.fresh_time()

        self.verticalLayout.addWidget(self.clock, 0, Qt.AlignCenter)
        
        self.timer1 = QTimer()
        self.timer1.setInterval(3600000)
        self.timer1.start()
        self.timer1.timeout.connect(self.fresh_weather)
        self.fresh_weather()

        self.thread = Detect_Worker(self.cap)
        self.thread.recog.connect(self.auto_detect)
        self.thread.sleep_down()
        self.thread.start()
        

    def fresh_weather(self):
        try:
            location = self.get_position(self.get_local_ip())
            if location['county'] != 'XX':
                self.label_2.setText('Location：'+location['country']+' '+location['region']+' '+location['city']+' '+location['county'])
                position = location['county']
            else:
                self.label_2.setText('Location：'+location['country']+' '+location['region']+' '+location['city'])
                position = location['city']
            url = 'http://wthrcdn.etouch.cn/weather_mini?city=%s' % position 
            info = requests.get(url).json()
            weather = info['data']['forecast'][0]['type']
            if weather == '暴雨':
                path = './application/uipy/picture/h1.png'
            elif weather =='雷阵雨':
                path = './application/uipy/picture/h2.png'
            elif weather =='多云':
                path = './application/uipy/picture/h7.png'
            elif weather =='晴':
                path = './application/uipy/picture/h8.png'
            elif weather =='雾':
                path = './application/uipy/picture/h10.png'
            elif weather =='小雨':
                path = './application/uipy/picture/g11.png'
            elif weather =='阴':
                path = './application/uipy/picture/h13.png' 
            elif weather =='大雨':
                path = './application/uipy/picture/g3.png'  
            elif weather =='中雨':
                path = './application/uipy/picture/g13.png'
            elif weather =='小雪':
                path = './application/uipy/picture/h11.png'
            elif weather =='中雪':
                path = './application/uipy/picture/g12.png'
            elif weather =='大雪':
                path = './application/uipy/picture/g2.png' 
            elif weather.find('阵雨') >=0:
                path = './application/uipy/picture/h6.png'
            png = QPixmap(path)
            self.label.setPixmap(png)
            self.label_3.setText('Weather：'+ weather)
            self.label_4.setText('Air temperature：'+info['data']['forecast'][0]['low']+'~'+info['data']['forecast'][0]['high'])
            time = QDateTime.currentDateTime()
            self.label_5.setText('Update-time：'+time.toString('yyyy-MM-dd hh:mm:ss'))
        except:
            self.label_5.setText('no Internet! update failed!')

    def get_position(self,ip):
        url = 'http://ip.taobao.com/service/getIpInfo.php?ip=%s'% ip
        info = requests.get(url).json()
        ##print(info['data']['county'])
        return info['data']

    def get_local_ip(self):
        req=requests.get("http://txt.go.sohu.com/ip/soip")
        for i in req:
            get = i.decode()
            ip=re.findall(r'\d+.\d+.\d+.\d+', get)
            if len(ip) != 0:    
                return ip[0]
       
    def fresh_time(self) -> None:
        now = datetime.datetime.now()
        self.clock.date = [now.year, now.month, now.day, now.weekday()]
        self.clock.time = [now.hour, now.minute, now.second]

    def reco(self):
        if self.models ==[]:
            init_thread = Update_Worker()
            init_thread.up.connect(self.model_update)
            init_thread.start()
        try:
            self.thread.sleep_down()
        except:
            pass
        if self.recogn == False and self.init == False:
            self.recogn = True
            self.recog_logger.info('Face-recognize beginn to work...')
            try:
                recog = recog_function(self.cap,self.sys_logger,self.recog_logger,self.models[0],self.models[1])
                self.sys_logger.info('Do to face-recognize...')
                recog.exec_()
                del recog
            except:
                self.showMessageBox_critical('Error','Camera Error')
        else:
            self.showMessageBox_info('Info','Auto-Detect has been started!')
        try:
            self.thread.wake_up()
        except:
            pass

    def manage(self):
        self.showNormal()
        self.thread.sleep_down()
        load = load_function(self.sys_logger)
        load.exec_()
        if load.value == 0:
            del load
            self.sys_logger.warning('Quit to load manage-site!')
        else:
            del load
            self.sys_logger.info('Load in manage-site!')
            try:
                mana = manage_function(self.cap,self.sys_logger)
                mana.setWindowModality(Qt.ApplicationModal)
                mana.exec_()
                del mana
                self.pushButton.setEnabled(False)
                self.init = True
                init_thread = Update_Worker()
                init_thread.up.connect(self.model_update)
                init_thread.start()
            except:
                self.showMessageBox_critical('Error','Camera Error!')
        self.showFullScreen()

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
        msgBox.button(QMessageBox.Ok).animateClick(3000)  
        msgBox.exec_()
        del msgBox
    
    def auto_detect(self,recog):
        if recog == -1:
            self.showMessageBox_critical("Error","Unable to open camera, please check and restart device!")
            self.sys_logger.error('\nUnable to open camera, please check and restart device!\n')
        elif recog ==0:
            self.showMessageBox("Error","Unable to read camera's data stream!")
            self.sys_logger.error('\nUnable to read camera\'s data stream! Please check and restart it!\n')
        elif recog ==1:
            if self.recogn:
                self.thread.sleep_down()
                try:
                    recog = recog_function(self.cap,self.sys_logger,self.recog_logger,self.models[0],self.models[1])
                    self.sys_logger.info('Do to face-recognize')
                    recog.exec_()
                    if recog.reg == False:
                        self.recogn = False
                    else:
                        self.thread.wake_up()
                    del recog
                except:
                    self.showMessageBox_critical('Error','Camera Error!')
    
    def model_update(self,rt,models):
        if rt == -2:
            self.showMessageBox_critical("Error","Unable to load face detect data set")
        if rt == -1:
            self.showMessageBox_critical("Error","Unable to load face recog data set")
        if rt == 1:
            self.models.append(models[0])
            self.models.append(models[1])
            self.init = False
            self.pushButton.setEnabled(True)

## 辅助线程，检测摄像头前有没有人脸
class Detect_Worker(QThread):
    recog = QtCore.pyqtSignal(int)

    def __init__(self,cap,parent = None):
        super(Detect_Worker,self).__init__(parent)
        self.cap = cap
        self.pause = False
        self.working = True

    def sleep_down(self):
        self.pause = True
    
    def wake_up(self):
        self.pause = False
        
    def run(self):
        rt = -1

        if not self.cap.isOpened():
            rt = -1
            self.working = False
            self.recog.emit(rt)
        
        face_cascade = cv2.CascadeClassifier()
        if not face_cascade.load(cv2.samples.findFile('./face_data/haarcascade_frontalface_alt.xml')):
            rt = -2
            self.pause = True
            self.recog.emit(rt)

        while self.working==True:
            rt = 1
            if self.pause == False:
                ret,frame = self.cap.read()

                if not ret:
                    rt = 0
                    self.pause = True
                    self.recog.emit(rt)

                faces = detectAndDisplay(frame, face_cascade)
            else:
                faces = ()
            if len(faces) >=1:
                self.recog.emit(rt)
            self.sleep(AUTO_DETECT)

## 初始化的时候预先加载数据集
class Update_Worker(QThread):
    up = QtCore.pyqtSignal(int,list)

    def __init__(self,parent = None):
        super(Update_Worker,self).__init__(parent)
    
    def run(self):
        rt = 1
        models = []
        face_cascade = cv2.CascadeClassifier()
        if not face_cascade.load(cv2.samples.findFile('./face_data/haarcascade_frontalface_alt.xml')):
            rt = -2
            self.up.emit(rt,models)
        else:
            models.append(face_cascade)

        recognizer = cv2.face_LBPHFaceRecognizer()
        model = recognizer.create()
        if not cv2.samples.findFile('./face_data/MyFaceLBPHModel.xml'):
            rt = -1
            self.up.emit(rt,models)
        else:
            model.read('./face_data/MyFaceLBPHModel.xml')
            models.append(model)
        
        if rt == 1:
           self.up.emit(rt,models) 
