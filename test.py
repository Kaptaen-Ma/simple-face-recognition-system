#!/usr/bin/python
# -*- coding:utf-8 -*- 
import os
import sqlite3
import datetime
import cv2
import numpy
import json
import requests
import re
import time
import xlrd

def create_csv(count):
    f = open('./faces/at.csv','w+',encoding='utf-8')
    nr = 1
    while (nr<count+1):
        ls = os.listdir('./faces/s'+str(nr))
        for i in ls:
            f.writelines(os.path.abspath('.')+'./faces/s'+str(nr)+'/'+i+';'+str(nr)+'\n')
        nr += 1

def face_info_append(martrikelnr,name):
        f = open('./faces/a.txt', mode='r+', encoding='utf-8')
        a = f.readline()
        b = str(int(a)+1)
        f.seek(0,2)
        f.writelines(b+';'+martrikelnr+';'+name+'\n')
        f.seek(0)
        f.writelines(b)
        f.close()
        return int(b)

def face_vor(count):
    nr = 0
    while(nr<count):
        face_info_append('*','*')
        nr += 1

def insert_ch(name,martrikelnr):
    conn = sqlite3.connect('./face_register/register.db')
    c = conn.cursor()
    dt = datetime.datetime.now()

    cursor = c.execute('INSERT INTO face (name, matrikelnummer,time) VALUES (\"'+name+'\",\"'+martrikelnr+'\",'+dt.strftime("%Y%m%d")+')')

    conn.commit()
    conn.close()

'''def update():
        faces=[]
        labels=[]
        path = './temp'
        imagePaths = [os.path.join(path,f) for f in os.listdir(path)]
        for imagePath in imagePaths:
            img = cv2.imread(imagePath)
            faces.append(img)
            labels.append(label)
        test = cv2.imread('D:\\Facerecognize\\orl_faces\\s42\\1.jpg')
        test = cv2.cvtColor(test, cv2.COLOR_BGR2GRAY)
        trainer = cv2.face_LBPHFaceRecognizer()
        model = trainer.create()
        print(1)
        model.read('./face_data/MyFaceLBPHModel.xml')
        print(1)
        ##trainer.update(faces,labels)
        lab,confidence = model.predict(test)
        print(1)
        print(lab)'''

def update_all():
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
        print(imagePaths)
        print(labels)
        trainer = cv2.face_LBPHFaceRecognizer()
        model = trainer.create()
        model.train(faces,numpy.array(labels))
        model.save('./MyFaceLBPHModel.xml')
        print(1)

def get_weather(position):
    url = 'http://wthrcdn.etouch.cn/weather_mini?city=%s' % position 
    info = requests.get(url).json()
    print(info)

def get_position(ip):
    url = 'http://ip.taobao.com/service/getIpInfo.php?ip=%s'% ip
    info = requests.get(url).json()
    ##print(info['data']['county'])
    return info['data']['city']

def get_local_ip():
    req=requests.get("http://txt.go.sohu.com/ip/soip")
    for i in req:
        get = i.decode()
        ip=re.findall(r'\d+.\d+.\d+.\d+', get)
        if len(ip) != 0:
            return ip[0]

def query_record(rowscount):
    record = []
    conn = sqlite3.connect('./face_register/register.db')
    c = conn.cursor()
    cur = c.execute('SELECT name,matrikelnummer, time from face')
    res = cur.fetchall()
    conn.close()
    print(len(res))
    row_sum = len(res)
    if rowscount > row_sum:
        leaf = []
        for row in res:
            leaf.append(row)
        record.append(leaf)
        return record
    else:
        leafscount = ((int)(row_sum/rowscount))+1
        print(leafscount)
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
        return record
    '''for row in cur.fetchall():
        print(row)'''
    

'''data = xlrd.open_workbook('./test_addin.xlsx')
table = data.sheets()[0]
names = data.sheet_names() 
nrows = table.nrows
reslut_row = table.row(0)

ncols = table.ncols
result_col = table.col_values(0) 
print(result_col[0])
col_names = table.row_values(0)
print(col_names)
for a in col_names:
    if a == 'name':
        result_col_name = table.col_values(col_names.index(a))
        print(result_col_name)
    elif a == 'std_nr':
        result_col_stdnr = table.col_values(col_names.index(a))
        print(result_col_stdnr)
    elif a == 'class':
        result_col_class = table.col_values(col_names.index(a))
        print(result_col_class)
if len(result_col_stdnr) == 1 or len(result_col_stdnr) == 0:
    print("No data in file!")
else:
    try:
        conn = sqlite3.connect('./face_register/register.db')
        conn.text_factory=str
        c = conn.cursor()
        for a in range(len(result_col_stdnr)):
            if a != 0:
                cursor = c.execute('INSERT INTO add_info (name, std_nr, class) VALUES (\"'+result_col_name[a]+'\",\"'+str(result_col_stdnr[a])+'\",'+result_col_class+')')
        conn.commit()
        conn.close()
    except:
        print('error')
    conn = sqlite3.connect('./face_register/register.db')
    conn.text_factory=str
    c = conn.cursor()
    for a in range(len(result_col_stdnr)):
        if a != 0:
            cursor = c.execute('INSERT INTO add_info (name, std_nr, class) VALUES (\"'+str(result_col_name[a])+'\",\"'+str(result_col_stdnr[a])+'\",\"'+str(result_col_class[a])+'\")')
    conn.commit()
    conn.close()'''

def mkdir():
    os.mkdir('./temp/stest')

def del_temp(path):
    ls = os.listdir(path)
    for i in ls:
        c_path = os.path.join(path,i)
        print(c_path)
        if os.path.isdir(c_path):
            del_temp(c_path)
            os.rmdir(c_path)  
        else:
            os.remove(c_path)
    del ls


la = [[1,21,3],[4,5,6],[5,31,2]]
def rm_list(a):
    a.remove([4,5,6])

rm_list(la)
    