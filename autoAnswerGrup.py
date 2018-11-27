#!/usr/bin/python
#coding=UTF-8
import itchat
from itchat.content import *
import re
import ctypes  
import time
import os
import sys

pathFloder = os.path.dirname(__file__)
DllFilePath = os.path.join(pathFloder,"crptyOK.dll")
#f = open(pathFloder+"\\"+"log.txt","w")
WechatGroupname = "AI"

#@itchat.msg_register([PICTURE,TEXT],isGroupChat=True)
@itchat.msg_register([PICTURE,TEXT],isGroupChat=True)
def simple_reply(msg):
    #匹配需要回复的关键字
    #【求设备密码12345678】
    print (msg['Content'])
    if msg['Content'][0:5] == "求设备密码":
       #取出设备号
       devid = re.sub("\D", "", msg['Content'])
       if len(devid) == 8:     
           devid_b = devid.encode("utf-8")  
           #确定需要发送的群
           rooms = itchat.search_chatrooms(WechatGroupname)
           userName = rooms[0]['UserName']
           print (userName)
#           print (msg['ActualNickName'])
           #取出当前时间
           nowtime=time.strftime('%Y%m%d',time.localtime(time.time()))
           nowtime_b = nowtime.encode("utf-8")
           #输入输出参数
           strin = devid_b+nowtime_b
           strkey = b"000000"
           #调用C库
           so = ctypes.cdll.LoadLibrary   
           lib = so(DllFilePath)
           lib.get_lock_code(strin,strkey)
           print(strkey) #最终的key
           #发送微信到专门的群上
           itchat.send('@%s %s '%(msg['ActualNickName'],strkey.decode()),toUserName=userName)
#           itchat.send('%s'%(strkey),toUserName=userName)
           f = open(pathFloder+"\\"+"log.txt","w")
           f.write(msg['ActualNickName'] +" "+ nowtime + "\n")
           f.close()
itchat.auto_login()#enableCmdQR=True 可以在命令行显示二维码
itchat.run()
