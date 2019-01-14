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
import tkinter as tk
import color
import kefuIF

#只需要修改下面的群名就可以了
WechatGroupname = "驾培旗舰版授权码获取"
WechatGroupname4G = "维尔前端问题自动回复"
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
        if msg["isAt"]:
            clr.print_red_text (msg['ActualNickName'].translate(non_bmp_map))
            clr.print_red_text (msg['User']['NickName'].translate(non_bmp_map)+" ")
            clr.print_red_text(" " + nowtime_ymdhms)
            clr.print_red_text (msg['Content'].translate(non_bmp_map)+"\n")           
        else:
            print (msg['ActualNickName'].translate(non_bmp_map))
            print (msg['User']['NickName'].translate(non_bmp_map)+" ",end="")
            print(" " + nowtime_ymdhms)
            print (msg['Content'].translate(non_bmp_map)+"\n")
        #将聊天记录记录到各自的文件中
        f = open(pathFloder+"\\"+msg['User']['NickName'].translate(non_bmp_map)+".txt","a+",encoding='utf-8')
        f.write(msg['ActualNickName'].translate(non_bmp_map)+" ")
        f.write(" " + nowtime_ymdhms+" ")
        f.write(msg['User']['NickName'].translate(non_bmp_map)+"\n")
        f.write(msg['Content'].translate(non_bmp_map)+"\n"+"\n")
        f.close()

        #以下是自动回复客服机器人的逻辑（驾培计时设备中一些常见的问题）
        if msg['User']['NickName'] == WechatGroupname4G:
            answer = kefuIF.answer(msg['Content'])
            #发送微信到专门的群上
            rooms = itchat.search_chatrooms(WechatGroupname4G)
            userName = rooms[0]['UserName']
            itchat.send('@%s %s '%(msg['ActualNickName'],answer),toUserName=userName)
            return 
        
        #以下是设备密码群的逻辑
        if msg['User']['NickName'] == WechatGroupname:    
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
        clr.print_red_text(msg['User']['NickName'].translate(non_bmp_map)+" ")
#        print (msg['ActualNickName'].translate(non_bmp_map))
        clr.print_red_text(msg['Content'].translate(non_bmp_map))
    except Exception as e:
        logging.exception(e)    

#接收朋友的图片信息
@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
def download_files(msg):
    try:
        path = os.path.join(pathFloder,msg['User']['NickName'].translate(non_bmp_map))
        makedir(path)
        msg.download(os.path.join(path,msg.fileName))
    except Exception as e:
        logging.exception(e)  

#接收群的图片信息
@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO],isGroupChat=True)
def download_files_frome_group(msg):
    try:
        path = os.path.join(pathFloder,msg['User']['NickName'].translate(non_bmp_map))
        makedir(path)
        msg.download(os.path.join(path,msg.fileName))
    except Exception as e:
        logging.exception(e) 

#@itchat.msg_register([TEXT],isFriendChat=True,isGroupChat=True)
#定义回复函数，回复是，先输入想要回复的人或群，然后输入一个空格，再输入回复消息即可回复。
def mes_select_reply(event):
    try:
        replymessage=""
        replymessage= E1.get()
        E1.delete(0, tk.END)  # 删除所有值
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
                 return
        #想要回复的内容
        content =  replymessage.split(" ",1)[1]
        print("@" + name0 +" "+content+"\n" )
        itchat.send("%s"%(content),toUserName=userName)
    except Exception as e:
        logging.exception(e) 
#创建文件夹
def makedir(path):
    # 去除首位空格
    path=path.strip()
    # 去除尾部 \ 符号
    path=path.rstrip("\\")
    isExists=os.path.exists(path)
     # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(path) 
        print (path+' 创建成功')
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
#       print (path+' 目录已存在')
        return False
#登录微信
def itdo():
    itchat.auto_login()#enableCmdQR=True 可以在命令行显示二维码
    itchat.run()

t1 = threading.Thread(target=itdo) #开启并行线程
#t.setDaemon(True)
t1.start()

#设置颜色
clr = color.Color()
clr.print_red_text('red')


#创建界面
chatframe = tk.Tk("消息回复")
#chatframe.geometry("500x50")
E1 = tk.Entry(chatframe,width=65)
#给输入框绑定按键监听事件<Key>为监听任何按键 <Key-x>监听其它键盘，如大写的A<Key-A>、回车<Key-Return>
E1.bind('<Key-Return>', mes_select_reply)
E1.pack(side = tk.LEFT)
B1 = tk.Button(chatframe,text = "发送",command = mes_select_reply)
B1.pack(side = tk.RIGHT)
chatframe.mainloop()





