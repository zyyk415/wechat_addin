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
import threading

#只需要修改下面的群名就可以了
WechatGroupname = "驾培旗舰版授权"
No = 0

#取得当前文件的目录
pathFloder = os.path.dirname(__file__)
DllFilePath = os.path.join(pathFloder,"crpty.dll")

non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)

#@itchat.msg_register([TEXT],isFriendChat=True,isGroupChat=True)
@itchat.msg_register([TEXT],isGroupChat=True)
def simple_reply(msg):
    global non_bmp_map
    #匹配需要回复的关键字
    #【求设备密码12345678】
    try:
        #取出当前时间
        nowtime=time.strftime('%Y%m%d',time.localtime(time.time()))
        nowtime_ymdhms = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        nowtime_b = nowtime.encode("utf-8")
        print (msg['User']['NickName'].translate(non_bmp_map)+" ",end="")
        print (msg['ActualNickName'].translate(non_bmp_map),end="")
        print(" " + nowtime_ymdhms)
        print (msg['Content'].translate(non_bmp_map)+"\n")
        #将聊天记录记录到各自的文件中
        f = open(pathFloder+"\\"+msg['User']['NickName'].translate(non_bmp_map)+".txt","a+",encoding='utf-8')
        f.write(msg['User']['NickName'].translate(non_bmp_map))
        f.write(msg['ActualNickName'].translate(non_bmp_map))
        f.write(" " + nowtime_ymdhms)
        f.write(msg['Content'].translate(non_bmp_map)+"\n")
        f.close()

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
               #输入输出参数
               strin = devid_b+nowtime_b
               strkey = b"000000"
               #调用C库
               so = ctypes.cdll.LoadLibrary   
               lib = so(DllFilePath)
               lib.get_lock_code(strin,strkey)
               #发送微信到专门的群上
               itchat.send('@%s %s '%(msg['ActualNickName'],strkey.decode()),toUserName=userName)
               print('@%s %s '%(msg['ActualNickName'].translate(non_bmp_map),strkey.decode()))
               f = open(pathFloder+"\\"+"log.txt","a+",encoding='utf-8')
               f.write(str(No)+" "+msg['ActualNickName'] +" "+ nowtime_ymdhms +" "+ devid + "\n")
               f.close()
    except Exception as e:
        logging.exception(e)

#接收朋友的消息
@itchat.msg_register([TEXT],isFriendChat=True)
def simple_friend_reply(msg):
    global non_bmp_map
    try:
        print (msg['User']['NickName'].translate(non_bmp_map)+" ",end="")
#        print (msg['ActualNickName'].translate(non_bmp_map))
        print (msg['Content'].translate(non_bmp_map))
    except Exception as e:
        logging.exception(e)    

#接收朋友的图片信息
#@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
#def download_files(msg):
#    try:
#        msg.download(os.path.join(pathFloder,msg.fileName))
#        typeSymbol = {
#            PICTURE: 'img',
#            VIDEO: 'vid', }.get(msg.type, 'fil')
#        return '@%s@%s' % (typeSymbol, msg.fileName)
#    except Exception as e:
#        logging.exception(e)  
#
#接收群的图片信息
#@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO],isGroupChat=True)
#def download_files_frome_group(msg):
#    try:
#        msg.download(os.path.join(pathFloder,msg.fileName))
#        typeSymbol = {
#            PICTURE: 'img',
#            VIDEO: 'vid', }.get(msg.type, 'fil')
#        return '@%s@%s' % (typeSymbol, msg.fileName)
#    except Exception as e:
#        logging.exception(e) 

#@itchat.msg_register([TEXT],isFriendChat=True,isGroupChat=True)
#定义回复函数，回复是，先输入想要回复的人或群，然后输入一个空格，再输入回复消息即可回复。
def mes_select_reply():
    while(1):
        try:
#            time.sleep(3) 不需要停止
            replymessage=""
            replymessage= input()
            #想要回复的对象 （群名或好友名称）
            name0 = replymessage.split()[0]
            #通过好友的昵称找到username
            userName0 = itchat.search_friends(name=name0)
            if userName0 != []:
                userName = userName0[0]["UserName"]
            else: 
                #通过群名找到username
                rooms = itchat.search_chatrooms(name0)
                if rooms != []:
                    userName = rooms[0]['UserName']
                else:
                    continue  
            #想要回复的内容
            content =  replymessage.split(" ",1)[1]
            print("@" + name0 +" "+content+"\n" )
            itchat.send("%s"%(content),toUserName=userName)
        except Exception as e:
            logging.exception(e) 

def itdo():
    itchat.auto_login()#enableCmdQR=True 可以在命令行显示二维码
    itchat.run()
    
t = threading.Thread(target=mes_select_reply) #开启并行线程
#t.setDaemon(True)
t.start()
t1 = threading.Thread(target=itdo) #开启并行线程
#t.setDaemon(True)
t1.start()



