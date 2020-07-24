人脸录入UI程序
---------

这是专为人脸识别程序所需训练数据集而管理采集人脸的UI程序

用户名：root
密码：admin

该UI的功能：
1、查看对应人脸识别日志信息；
2、录入人脸；
3、删除人脸的功能；
4、修改用户名密码的功能；
5、进行人脸识别的功能；
6、查看时间
7、查看天气预报

--当使用人脸识别时，除非主动退出，程序会一直执行，每识别一次暂停0.8s

--人脸录入可以分为三步：

1、输入姓名、学号，点击开始
2、当左下角提示可以拍摄时进行拍摄，拍摄到一定张数时，点击保存，进行保存
3、人脸录入完成，退出

--删除人脸：

先选择学号，然后和会产生对应的记录
选择记录删除

--查看天气：

1、通过request获得当地的地理位置
2、通过得到的地理位置再用request查询当地的天气
3、根据查到的天气数据切换gif
4、每30~60min查询一次

程序结构：
采用界面与功能分离的模式

界面             | 功能               | 描述
main.py          | main.py           | 主界面
    |--clock.py                         |--主界面的时钟
manage.py        | managefunction.py | 管理界面
load.py          | loadfunction.py   | 登陆界面
delface.py       | deletefunction.py | 删除人脸界面
check_photo.py   | checkfunction.py  | 查看记录中对应拍摄的人脸照片
face.py          | facefunction.py   | 录入人脸界面
recog.py         | recogfunction.py  | 人脸识别界面
usermodify.py    | modifyfunction.py | 修改用户名密码界面

目录结构：
|--application: 应用py文件
|  |--uipy： PyQt5界面
|     |--picture:  应用到的图片素材
|
|--face_data: 人脸数据集
|
|--face_register: sqlite数据库
|
|--faces: 存放拍摄的人脸
|
|--temp: 存放拍摄中的缓存

程序入口：
main.py