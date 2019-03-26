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
from tkinter import scrolledtext        # 导入滚动文本框的模块
import kefu.kefuIF
from PIL import Image

#只需要修改下面的群名就可以了
WechatGroupname = "驾培旗舰版授权码获取"
WechatGroupname4G = "维尔前端问题自动回复"
No = 0

#取得当前文件的目录
pathFloder = os.path.dirname(__file__)
DllFilePath = os.path.join(pathFloder,"crpty.dll")
logPath = os.path.join(pathFloder,"wechatLOG")

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
              print ("IS @")
        scr.insert(tk.END, msg['ActualNickName'].translate(non_bmp_map)+"\n")
        scr.insert(tk.END, msg['User']['NickName'].translate(non_bmp_map)+" ")
        scr.insert(tk.END, " " + nowtime_ymdhms+"\n")
        scr.insert(tk.END, msg['Content'].translate(non_bmp_map)+"\n")
        scr.insert(tk.END,"\n")
        scr.see(tk.END)

            
        #将聊天记录记录到各自的文件中
        f = open(logPath+"\\"+msg['User']['NickName'].translate(non_bmp_map)+".txt","a+",encoding='utf-8')
        f.write(msg['ActualNickName'].translate(non_bmp_map)+" ")
        f.write(" " + nowtime_ymdhms+" ")
        f.write(msg['User']['NickName'].translate(non_bmp_map)+"\n")
        f.write(msg['Content'].translate(non_bmp_map)+"\n"+"\n")
        f.close()

        #以下是自动回复客服机器人的逻辑（驾培计时设备中一些常见的问题）
        if msg['User']['NickName'] == WechatGroupname and msg["isAt"]:
            if msg['Content'] == "@研发-郑银尧" or msg['Content'] == "@研发-郑银尧\u2005":
                answer = "您好，欢迎使用维尔自动回复系统。您可以直接输入【求设备密码12345678】的格式来获取操作密码，也可以【@我 + 问题】来查找一些简单的问题。密码不正确请确认设备时间或私聊我。"
            else:
                answer = kefu.kefuIF.answer(msg['Content'][5:])
            #发送微信到专门的群上
            rooms = itchat.search_chatrooms(WechatGroupname)
            userName = rooms[0]['UserName']
            itchat.send('@%s %s '%(msg['ActualNickName'],answer),toUserName=userName)
            scr.insert(tk.END,"@"+msg['ActualNickName']+answer+"\n")
            scr.insert(tk.END,"\n\n")
            scr.see(tk.END)
            return 
        
        #以下是设备密码群的逻辑
        if msg['User']['NickName'] == WechatGroupname:    
            if msg['Content'][0:5] == "求设备密码" or  msg['Content'][0:1] == "求":
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
                   scr.insert(tk.END, "@" + msg['ActualNickName'].translate(non_bmp_map) + strkey.decode())
                   scr.insert(tk.END,"\n\n")
                   scr.see(tk.END)

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
        #打印朋友的名字
        scr.insert(tk.END,msg['User']['NickName'].translate(non_bmp_map))
        scr.insert(tk.END,"\n")
        scr.insert(tk.END,msg['Content'].translate(non_bmp_map))
        scr.insert(tk.END,"\n")
        scr.insert(tk.END,"\n")
        scr.see(tk.END)
    except Exception as e:
        logging.exception(e)    

#接收朋友的图片信息
@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
def download_files(msg):
    try:
        path = os.path.join(logPath,msg['User']['NickName'].translate(non_bmp_map))
        makedir(path)
        print(msg.fileName + "\n")
        scr.insert(tk.END, msg['User']['NickName'].translate(non_bmp_map)+"\n")

        filepath = os.path.join(path,msg.fileName)
        msg.download(filepath)
        #转换接收到的图片未gif
        changepath = image2gif(filepath)
        #显示图片
        mes_image_display(scr,changepath)
    except Exception as e:
        logging.exception(e)  

#接收群的图片信息
@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO],isGroupChat=True)
def download_files_frome_group(msg):
    try:
        path = os.path.join(logPath,msg['User']['NickName'].translate(non_bmp_map))
        makedir(path)
        print(msg.fileName + "\n")
    #    scr.insert(tk.END, msg.fileName + "\n" )
    #    scr.insert(tk.END,"\n\n")
        #打印群中朋友的名字  
        scr.insert(tk.END, msg['ActualNickName'].translate(non_bmp_map)+"\n")
        scr.insert(tk.END, msg['User']['NickName'].translate(non_bmp_map)+"\n")

        filepath = os.path.join(path,msg.fileName)
        msg.download(filepath)
        #转换接收到的图片未gif
        changepath = image2gif(filepath)
        #显示图片
        mes_image_display(scr,changepath) 
    except Exception as e:
        logging.exception(e) 

#@itchat.msg_register([TEXT],isFriendChat=True,isGroupChat=True)
#定义回复函数，回复是，先输入想要回复的人或群，然后输入一个空格，再输入回复消息即可回复。
def mes_select_reply(event):
    try:
        replymessage=""
        replymessage = text2.get("0.0","end")
        text2.delete('0.0','end')  # 删除所有值
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
        scr.insert(tk.END, "\n"+"@" + name0 +" "+content+"\n\n" )
        scr.insert(tk.END,"\n")
        itchat.send("%s"%(content),toUserName=userName)
        scr.see(tk.END)
    except Exception as e:
        logging.exception(e) 

#发文件
def mes_file_send(event):
    try:
        replymessage=""
        replymessage= E2.get()
        E2.delete(0, tk.END)  # 删除所有值
        E2.icursor(0)
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
        scr.insert(tk.END, "@" + name0 +" "+content+"\n\n" )
        print(itchat.send_file(content,toUserName=userName))
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
#-------------------图片显示处理--------------------------------------
#其他格式的图片转换成gif格式的图片。
#参数：转换前的图片路径
#返回值：转换后的图片路径
def image2gif(filePath):
    im=Image.open(filePath)
 #   size = im.size
    out = im.resize((320, 240),Image.ANTIALIAS) #resize image with high-quali
    images=[]
#    images.append(Image.open('a1.png'))
#    images.append(Image.open('a2.png'))
    filePath1 = filePath.split(".")[0]
    savePath = filePath1+".gif"
    out.save(savePath, save_all=True, append_images=images,loop=1,duration=1,comment=b"aaabb")
    return savePath
 
#发图片
def mes_image_display(scr,ImagePath):
    path = image2gif(ImagePath)
    global photo
    photo = tk.PhotoImage(file=path)
    scr.image_create(tk.END, image=photo)#用这个方法创建一个图片对象，并插入到“END”的位置
    scr.insert(tk.END, "\n\n")
    scr.see(tk.END)

   # chatframe.mainloop()

def fun_timer():
    chatframe.update()
    chatframe.after(1000)


if __name__ == "__main__":

    t1 = threading.Thread(target=itdo) #开启并行线程
    #t.setDaemon(True)
    t1.start()

    timer = threading.Timer(1, fun_timer)
    timer.start()
    
    #设置颜色
    clr = color.Color()
    clr.print_red_text('red')
    
    #创建界面
    chatframe = tk.Tk("消息回复")
    #滚动窗口
    scr = scrolledtext.ScrolledText(chatframe, width=78, height=30, wrap=tk.WORD) 
    scr.pack()
    
    text2 = tk.Text(chatframe,height=5)
    text2.bind('<Key-Return>', mes_select_reply)
    text2.pack()
    
    E2 = tk.Entry(chatframe,width=80)
    #给输入框绑定按键监听事件<Key>为监听任何按键 <Key-x>监听其它键盘，如大写的A<Key-A>、回车<Key-Return>
    E2.bind('<Key-Return>', mes_file_send)
    E2.pack()
    
    chatframe.mainloop()





