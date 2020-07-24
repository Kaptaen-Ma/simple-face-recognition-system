import sys
from PyQt5 import QtCore,QtGui,QtWidgets
from PyQt5.QtCore import QCoreApplication,Qt,QThread
from PyQt5.QtWidgets import QApplication, QDialog,QMessageBox
from application.uipy.delface import Ui_Dialog
from application.checkfunction import check_function
from application.waitfunction import wait_function
import sqlite3
import os
import numpy
import cv2
import re

class delete_function(Ui_Dialog,QDialog):
    def __init__(self,log,parent = None):
        super(delete_function,self).__init__()
        self.setupUi(self)
        self.logger = log
        self.record = []
        self.leaf = 1
        self.currentleaf = 1
        try:
            self.record , self.leaf = self.query_record(9)
        except:
            self.showMessageBox_critical("Error","Unable to connect to database!")
            self.logger.error('\nUnable to connect to database!\n')
        self.model_append(self.record[self.currentleaf-1])
        self.pushButton.clicked.connect(self.query_stdnr)
        self.pushButton_2.clicked.connect(self.close)
        self.pushButton_3.clicked.connect(self.first_page)
        self.pushButton_4.clicked.connect(self.previous_page)
        self.pushButton_5.clicked.connect(self.next_page)
        self.pushButton_6.clicked.connect(self.last_page)
        self.pushButton_7.clicked.connect(self.jump_page)
        self.pushButton_8.clicked.connect(self.delete)
        self.tableView.customContextMenuRequested.connect(self.showContextMenu)
        self.tableView.doubleClicked.connect(self.check_photo)
        self.wait = wait_function()
    
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

    def jump_page(self):
        page = self.lineEdit_2.text()
        if page.isdigit():
            if int(page)<1 or int(page)>self.leaf:
                self.showMessageBox_critical('Error','Out of range!')
            else:
                self.currentleaf = int(page)
                self.model_append(self.record[self.currentleaf-1])
                self.label_2.setText('Page:%s'%str(self.currentleaf))
        else:
            self.showMessageBox_critical('Error','Please enter a number!')

    def query_record(self,rowscount):
        record = []
        conn = sqlite3.connect('./face_register/register.db')
        c = conn.cursor()
        cur = c.execute('SELECT name,matrikelnummer, time, label from face')
        res = cur.fetchall()
        conn.close()
        row_sum = len(res)
        if rowscount >= row_sum:
            leaf = []
            for row in res:
                leaf.append(row)
            record.append(leaf)
            return record, 1
        else:
            leafscount = ((int)(row_sum/rowscount))+1
            self.label_3.setText('Total:%s'%str(leafscount))
            i = 0
            while(i<leafscount):
                count = 0
                leaf = []
                while(count<rowscount):
                    row = i*rowscount+count
                    if( row < row_sum):
                        leaf.append(res[row])
                    else:
                        break
                    count += 1
                record.append(leaf)
                i += 1
            return record , leafscount

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
            deletelabel = self.record[self.currentleaf-1][currentrow][3]+40
            button = QMessageBox.question(self,"Question","If you choose to delete, all the information will be deleted and the data set will be retrained,that might take a long time!",QMessageBox.Ok|QMessageBox.Cancel,QMessageBox.Cancel)
            if button == QMessageBox.Ok:   
                self.delete_dir(deletelabel)
                conn = sqlite3.connect('./face_register/register.db')
                c = conn.cursor()
                cur = c.execute('DELETE from face where label ='+ str(deletelabel-40))
                conn.commit()
                conn.close()
                update = Update_Worker()
                update.tip.connect(self.update_tip)
                update.start()
                self.logger.info('delete the information of the person(student number:'+self.record[self.currentleaf-1][currentrow][1]+')')
                self.wait.exec_()

                

    def check_photo(self):
        currentrow = self.tableView.selectionModel().currentIndex().row()
        if currentrow < len(self.record[self.currentleaf-1]):
            checklabel = self.record[self.currentleaf-1][currentrow][3]+40
            checkphoto = cv2.imread('./faces/s'+str(checklabel)+'/1.pgm')
            check = check_function(checkphoto,self.record[self.currentleaf-1][currentrow])
            check.setWindowModality(Qt.ApplicationModal)
            check.exec_()
            del check

    def face_info(self,matrikelnr):
        conn = sqlite3.connect('./face_register/register.db')
        c = conn.cursor()
        cur = c.execute('SELECT label from face where matrikelnummer =\"'+ matrikelnr+'\"')
        label = []
        for row in cur.fetchall():
            label.append(row[0])
        conn.close()
        return label
        
    def delete_dir(self,a):
        c_path = './faces/s'+str(a)
        ls = os.listdir(c_path)
        for i in ls:
            c_path2 = os.path.join(c_path,i)
            os.remove(c_path2)
        os.rmdir(c_path)  
    

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
    
    def update_tip(self,info):
        if info == 1:
            self.wait.close()
            self.showMessageBox_info("Info","Successfully deleted!")
            self.logger.warning('Dataset has been new train!')  
            self.record,self.leaf = self.query_record(9)
            self.first_page()

class Update_Worker(QThread):
    tip = QtCore.pyqtSignal(int)
    
    def __init__(self,parent = None):
        super(Update_Worker,self).__init__(parent)
    
    def run(self):
        self.update_all()
        self.tip.emit(1)

    def update_all(self):
        label = 1
        faces=[]
        labels=[]
        fpath = './faces'
        imagePaths = []
        ls = os.listdir(fpath)
        for fdir in ls:
            npath = os.path.join(fpath,fdir)
            num = re.findall('\d+',npath)
            label = int(num[0])
            for im in os.listdir(npath):
                imagePaths.append(os.path.join(npath,im))
                labels.append(label)
        for imagePath in imagePaths:
            img = cv2.imread(imagePath)
            img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            faces.append(img)
        trainer = cv2.face_LBPHFaceRecognizer()
        model = trainer.create()
        model.train(faces,numpy.array(labels))
        model.save('./face_data/MyFaceLBPHModel.xml')