#!/usr/bin/python
#-*-encoding:utf-8-*-
from __future__ import print_function
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QCoreApplication, QTimer,Qt
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
from application.uipy.addface import Ui_Dialog
from application.waitfunction import wait_function
from application.checkfunction import check_function
from application.addinfofunction import addinfo_function
from application.addfacefunction import addface_function
import sqlite3
import datetime
import xlrd

'''
    pushbutton1: Search
    pushbutton2: 第一页
    pushbutton3: 上一页
    pushbutton4: 下一页
    pushbutton5: 尾页
    pushbutton6: 开始拍摄
    pushbutton7: 导入excel
    pushbutton8: 退出
    pushbutton9: 保存
'''

class face_function(Ui_Dialog, QDialog):
    def __init__(self,cap,log,parent=None):
        super(face_function, self).__init__()
        
        self.setupUi(self)
        #新增
        self.model = None
        self.faces_info = []
        self.record = []
        self.face_total = 0
        self.leaf = 1
        self.currentleaf = 1
        #
        self.record , self.leaf = self.leaf_join(9)
        self.model_append(self.record[self.currentleaf-1])

        self.cap = cap
        self.logger = log
        self.del_temp('./temp')       
        self.pushButton.clicked.connect(self.query_stdnr)
        self.pushButton_2.clicked.connect(self.first_page)
        self.pushButton_3.clicked.connect(self.previous_page)
        self.pushButton_4.clicked.connect(self.next_page)
        self.pushButton_5.clicked.connect(self.last_page)
        self.tableView.customContextMenuRequested.connect(self.showContextMenu)
        self.tableView.doubleClicked.connect(self.check_photo)
        self.pushButton_6.clicked.connect(self.beginn)
        self.pushButton_8.clicked.connect(self.quit)
        self.pushButton_7.clicked.connect(self.imp_xls)
        self.pushButton_9.clicked.connect(self.save)
        self.pushButton_10.clicked.connect(self.delete)

        self.wait = wait_function()

        # 正脸检测
        self.face_cascade = cv2.CascadeClassifier()
        if not self.face_cascade.load(cv2.samples.findFile('./face_data/haarcascade_frontalface_alt.xml')):
            self.showMessageBox("Error","Unable to load face data set!")
            self.logger.error('\nUnable to load face data set!\n')
            self.quit()
        '''
        # 侧脸检测
        self.left_face_cascade = cv2.CascadeClassifier()
        if not self.left_face_cascade.load(cv2.samples.findFile('./face_data/haarcascade_profileface.xml')):
            self.showMessageBox("Error","Unable to load face data set!")
            self.logger.error('\nUnable to load face data set!\n')
            self.quit()''' 



    def model_append(self,leaf_record):
        model = QtGui.QStandardItemModel(9,3)
        model.setHorizontalHeaderLabels(['Name','Student Number','timer'])
        for row in range(9):
            for column in range(3):
                if row <len(leaf_record):
                    i = QtGui.QStandardItem(leaf_record[row][column])
                    model.setItem(row,column,i)
        self.tableView.setModel(model)
        self.tableView.setColumnWidth(0,237)
        self.tableView.setColumnWidth(1,237)
        self.tableView.setColumnWidth(2,237)
    
    def leaf_join(self,rowscount):
        record = []
        if rowscount >= self.face_total:
            leaf = []
            for row in self.faces_info:
                leaf.append(row)
            record.append(leaf)
            return record, 1
        else:
            leafscount = ((int)(self.face_total/rowscount))+1
            self.label_3.setText('Total:%s'%str(leafscount))
            i = 0
            while(i<leafscount):
                count = 0
                leaf = []
                while(count<rowscount):
                    row = i*rowscount+count
                    if( row < self.face_total):
                        leaf.append(self.faces_info[row])
                    else:
                        break
                    count += 1
                record.append(leaf)
                i += 1

    def query_stdnr(self):
        stdnr = self.lineEdit.text()
        count = 0
        for leaf in self.record:
            count += 1
            for row in leaf:
                if stdnr == row[1]:
                    self.currentleaf = count
                    self.model_append(self.record[self.currentleaf-1])
                    self.label_2.setText('Page:%s'%str(self.currentleaf))

    def first_page(self):
        self.currentleaf = 1
        self.model_append(self.record[self.currentleaf-1])
        self.label_2.setText('Page:%s'%str(self.currentleaf))

    def previous_page(self):
        if self.currentleaf > 1:
            self.currentleaf -= 1
            self.model_append(self.record[self.currentleaf-1])
            self.label_2.setText('Page:%s'%str(self.currentleaf))
        else:
            self.showMessageBox_info('Info','Already the first page')
    
    def next_page(self):
        if self.currentleaf < self.leaf:
            self.currentleaf +=1
            self.model_append(self.record[self.currentleaf-1])
            self.label_2.setText('Page:%s'%str(self.currentleaf))
        else:
            self.showMessageBox_info('Info','Already the last page!')
    
    def last_page(self):
        self.currentleaf = self.leaf
        self.model_append(self.record[self.currentleaf-1])
        self.label_2.setText('Page:%s'%str(self.currentleaf))

    def showContextMenu(self):  # 创建右键菜单
        self.tableView.contextMenu = QtWidgets.QMenu()
        self.Check = self.tableView.contextMenu.addAction('Check Photo')
        self.Del = self.tableView.contextMenu.addAction('Delete')
        # self.actionA = self.tableView.contextMenu.exec_(self.mapToGlobal(pos))  # 1
        self.tableView.contextMenu.popup(QtGui.QCursor.pos())  # 2菜单显示的位置
        self.Check.triggered.connect(self.check_photo)
        self.Del.triggered.connect(self.delete)
        # self.tableView.contextMenu.move(self.pos())  # 3
        self.tableView.contextMenu.show()
    
    def delete(self):
        currentrow = self.tableView.selectionModel().currentIndex().row()
        if currentrow < len(self.record[self.currentleaf-1]):
            deletelabel = self.record[self.currentleaf-1][currentrow][3]
            button = QMessageBox.question(self,"Question","If you choose to delete, all the information will be deleted and the data set will be retrained,that might take a long time!",QMessageBox.Ok|QMessageBox.Cancel,QMessageBox.Cancel)
            if button == QMessageBox.Ok:   
                self.delete_dir(deletelabel)
                for item in self.faces_info:
                    if item[3] == deletelabel:
                        self.faces_info.remove(item)
                        lastleaf = self.leaf
                        self.record , self.leaf = self.leaf_join(9)
                        if lastleaf>self.leaf and self.currentleaf == lastleaf:
                            self.currentleaf-1
                            self.model_append(self.record[self.currentleaf-1])
                        else:
                            self.model_append(self.record[self.currentleaf-1])
                self.showMessageBox_info('Info','Delete Sucessfully!')
                

    def delete_dir(self,a):
        c_path = './temp2/s'+str(a)
        ls = os.listdir(c_path)
        for i in ls:
            c_path2 = os.path.join(c_path,i)
            os.remove(c_path2)
        os.rmdir(c_path)
    
    def check_photo(self):
        currentrow = self.tableView.selectionModel().currentIndex().row()
        if currentrow < len(self.record[self.currentleaf-1]):
            checklabel = self.record[self.currentleaf-1][currentrow][3]
            checkphoto = cv2.imread('./temp2/s'+str(checklabel)+'/1.pgm')
            check = check_function(checkphoto,self.record[self.currentleaf-1][currentrow])
            check.setWindowModality(Qt.ApplicationModal)
            check.exec_()
            del check

    ## 要考虑时覆盖或者比较差异添加
    def imp_xls(self):
        fileName1, filetype = QFileDialog.getOpenFileName(self,
                  "选取文件",
                  "./",
                  "Excel Files (*.xlsx)")  #设置文件扩展名过滤,注意用双分号间隔
        if fileName1 != '':

            data = xlrd.open_workbook(fileName1)
            table = data.sheets()[0]
            col_names = table.row_values(0)
            result_col_name = []
            for a in col_names:
                if a == 'name':
                    result_col_name = table.col_values(col_names.index(a))
                elif a == 'std_nr':
                    result_col_stdnr = table.col_values(col_names.index(a))
                elif a == 'class':
                    result_col_class = table.col_values(col_names.index(a))
            
            if len(result_col_stdnr) == 1 or len(result_col_stdnr) == 0:
                self.showMessageBox("Error", "No data in file!")
            else:
                try:
                    conn = sqlite3.connect('./face_register/register.db')
                    conn.text_factory=str
                    c = conn.cursor()
                    for a in range(len(result_col_stdnr)):
                        if a != 0:
                            cursor = c.execute('INSERT INTO add_info (name, std_nr, class) VALUES (\"'+str(result_col_name[a])+'\",\"'+str(result_col_stdnr[a])+'\",\"'+str(result_col_class[a])+'\")')
                    conn.commit()
                    conn.close()
                except:
                    self.showMessageBox("Error","Unable to connect to database!")
                    self.logger.error('\nUnable to connect to database!\n')
                self.get_stdinfo()
            

    def quit(self):
        ##self.thread.__del__()
        if self.faces_info != []:
            button = QMessageBox.question(self,"Question","You have info not save, please choose save or not!",QMessageBox.Ok|QMessageBox.Cancel,QMessageBox.Cancel)
            if button == QMessageBox.Ok:
                self.save()
            else:
                self.del_temp('./temp2')
        self.close()
    
    def del_temp(self, path):
        ls = os.listdir(path)
        for i in ls:
            c_path = os.path.join(path,i)
            if os.path.isdir(c_path):
                self.del_temp(c_path)
                os.rmdir(c_path)
            else:
                os.remove(c_path)
        del ls

    def face_info_append(self,martrikelnr,name):
        try:
            conn = sqlite3.connect('./face_register/register.db')
        
            conn.text_factory=str
            c = conn.cursor()
            dt = datetime.datetime.now()

            cursor = c.execute('INSERT INTO face (name, matrikelnummer,time) VALUES (\"'+name+'\",\"'+martrikelnr+'\",'+dt.strftime("%Y%m%d")+')')

            conn.commit()
            a = cursor.lastrowid + 40
            conn.close()
            return a
        except:
            self.showMessageBox("Error","Unable to connect to database!")
            self.logger.error('\nUnable to connect to database!\n')
        
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

    '''def del_temp(self, path):
        ls = os.listdir(path)
        for i in ls:
            c_path = os.path.join(path,i)
            if os.path.isdir(c_path):
                self.del_temp(c_path)
            else:
                os.remove(c_path)
        del ls'''

    def beginn(self):
        addinfo = addinfo_function()
        addinfo.exec_()
        if addinfo.result() == QDialog.Accepted:
            self.del_temp('./temp')
            try:
                addface = addface_function(self.cap,self.face_cascade)
                addface.exec_()
                if addface.photo_num <15 :
                    self.del_temp('./temp')
                else:
                    face = []
                    face.append(addinfo.comboBox.currentText())
                    face.append(addinfo.comboBox_2.currentText())
                    dt = datetime.datetime.now()
                    face.append(dt.strftime("%Y%m%d"))
                    self.face_total += 1
                    face.append(self.face_total)
                    self.faces_info.append(face)
                    self.record , self.leaf = self.leaf_join(9)
                    self.label_3.setText('Total:'+str(self.leaf))
                    self.model_append(self.record[self.currentleaf-1])
                    shutil.copytree('./temp','./temp2/s'+str(self.face_total))
                    self.del_temp('./temp')
                    # 记录至列表并进行更新,移动到第二级缓存
                del addface
            except:
                self.showMessageBox('Error','Camera Error or data-set is destroyed')
        del addinfo

    def save(self):
        if self.face_cascade != []:
            self.label.setText('training... Please wait')
            labs = []
            for index in range(self.face_total):
                x = self.face_info_append(self.faces_info[index][0],self.faces_info[index][1])
                labs.append(x)
            print(labs)
            upd = Save_Worker(labs)
            upd.tip.connect(self.tip_save)
            #upd.result.connect(self.get_result)
            print(1)
            upd.start()
            self.wait.exec_()
  
    def tip_save(self,rt,model):
        if rt == 1:
            self.wait.close()
            self.faces_info.clear()
            self.face_total = 0
            self.record.clear()
            self.leaf = 1
            self.currentleaf = 1
            self.label_2.setText('Page:'+str(1))
            self.label_3.setText('Total:'+str(self.leaf))
            self.model_append(self.record)
            self.model = model[0]
            ##self.label.setText("Added successfully!")
            ##self.logger.info('success to add the face-data(student number:'+self.comboBox_2.currentText()+')')
            self.showMessageBox_info("Info","Added successfully!") 
    



class Save_Worker(QThread):
    tip = QtCore.pyqtSignal(int,list)

    def __init__(self,labs,parent=None):
        super(Save_Worker,self).__init__(parent)
        self.labs = labs
        self.model = []
    
    def __del__(self):
        self.quit()
        ##self.wait()
    
    def run(self):
        self.update()
        self.del_temp('./temp2')
        self.tip.emit(1,self.model)

    def update(self):
        faces=[]
        labels=[]
        fpath = './temp2'
        imagePaths = []
        ls = os.listdir(fpath)
        lab = 0
        for fdir in ls:
            lab += 1
            npath = os.path.join(fpath,fdir)
            shutil.copytree(npath,'./faces/s'+str(self.labs[lab-1]))
            for im in os.listdir(npath):
                imagePaths.append(os.path.join(npath,im))
                labels.append(self.labs[lab-1])
        for imagePath in imagePaths:
            img = cv2.imread(imagePath)
            img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            faces.append(img)
            ##labels.append(label)
        trainer = cv2.face_LBPHFaceRecognizer()
        model = trainer.create()
        model.read('./face_data/MyFaceLBPHModel.xml')
        model.update(faces,numpy.array(labels))
        model.save('./face_data/MyFaceLBPHModel.xml')
        self.model.append(model)

    def del_temp(self, path):
        ls = os.listdir(path)
        for i in ls:
            c_path = os.path.join(path,i)
            if os.path.isdir(c_path):
                self.del_temp(c_path)
                os.rmdir(c_path)
            else:
                os.remove(c_path)
        del ls
