#!/usr/bin/python
#coding=UTF-8
import itchat
from itchat.content import *
import re
import ctypes  
import time
import os
import sys
import logging

#只需要修改下面的群名就可以了
WechatGroupname = "驾培旗舰版授权"
No = 0

pathFloder = os.path.dirname(__file__)
DllFilePath = os.path.join(pathFloder,"crpty.dll")

non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)

#@itchat.msg_register([TEXT],isGroupChat=True)
@itchat.msg_register([TEXT],isGroupChat=True)
def simple_reply(msg):
    global non_bmp_map
    #匹配需要回复的关键字
    #【求设备密码12345678】
    try:
        print (msg['User']['NickName'].translate(non_bmp_map)+" ",end="")
        print (msg['ActualNickName'].translate(non_bmp_map))
        print (msg['Content'].translate(non_bmp_map))
        if msg['Content'][0:5] == "求设备密码":
           #取出设备号
           devid = re.sub("\D", "", msg['Content'])
           if len(devid) == 8:
               global No
               No = No + 1
               devid_b = devid.encode("utf-8")  
               #确定需要发送的群
               rooms = itchat.search_chatrooms(WechatGroupname)
               userName = rooms[0]['UserName']
#               print (userName)
               #取出当前时间
               nowtime=time.strftime('%Y%m%d',time.localtime(time.time()))
               nowtime_ymdhms = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
               nowtime_b = nowtime.encode("utf-8")
               #输入输出参数
               strin = devid_b+nowtime_b
               strkey = b"000000"
               #调用C库
               so = ctypes.cdll.LoadLibrary   
               lib = so(DllFilePath)
               lib.get_lock_code(strin,strkey)
#               print(strkey) #最终的key
#               print("\n")
               #发送微信到专门的群上
               itchat.send('@%s %s '%(msg['ActualNickName'],strkey.decode()),toUserName=userName)
               print('@%s %s '%(msg['ActualNickName'].translate(non_bmp_map),strkey.decode()))
               f = open(pathFloder+"\\"+"log.txt","a+")
               f.write(str(No)+" "+msg['ActualNickName'] +" "+ nowtime_ymdhms +" "+ devid + "\n")
               f.close()
    except Exception as e:
        logging.exception(e)
itchat.auto_login()#enableCmdQR=True 可以在命令行显示二维码
itchat.run()
