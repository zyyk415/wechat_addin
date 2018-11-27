#!/usr/bin/python
#coding=UTF-8
import itchat
import ctypes
import PIL
from itchat.content import *
import re
import time
import os

pathFloder = os.path.dirname(__file__)
DllFilePath = os.path.join(pathFloder,"crptyOK.dll")


d = {"V":["获取","请求","想要","恳求","跪求", "get", "给", "要", "给我"], "N_PWD":["密码", "秘密", "password"]}
def fuzzy_match(txt):
    """
    模糊判定请求密码命令
    :param txt:
    :return:
    """
    txt = match_v(txt)
    if txt is not None:
        return match_n(txt)
    return False


def match_v(txt):
    """
    判定动词
    :param txt: 文本
    :return:
    """
    v_list = d["V"]
    for v in v_list:
        v_index = txt.find(v)
        print(v_index)
        if v_index > -1:
            return txt[v_index + len(v):]
    return None

def match_n(txt):
    """
    判断名称
    :param txt:文本
    :return:
    """
    n_list = d["N_PWD"]
    for n in n_list:
        if txt.find(n) > -1:
            return True
    return False


@itchat.msg_register([PICTURE,TEXT],isGroupChat=True)
def simple_reply(msg):
    # 匹配需要回复的关键字
    #【求设备密码12345678】
    print(msg['Content'])

    if fuzzy_match(msg['Content']):
       #取出设备号
       devid = re.sub("\D", "", msg['Content'])
       if len(devid) == 8:
           devid_b = devid.encode("utf-8")
           # 确定需要发送的群
           rooms = itchat.search_chatrooms("AI小组")
           userName = rooms[0]['UserName']
           print (userName)
           # print (msg['ActualNickName'])
           #取出当前时间
           nowtime =time.strftime('%Y%m%d',time.localtime(time.time()))
           nowtime_b = nowtime.encode("utf-8")
           #输入输出参数
           strin = devid_b + nowtime_b
           strkey = b"000000"
           #调用C库
           so = ctypes.cdll.LoadLibrary
           lib = so(DllFilePath)
           lib.get_lock_code(strin,strkey)
           print(strkey) #最终的key
           #发送微信到专门的群上
           itchat.send('@%s %s '%(msg['ActualNickName'],strkey.decode()),toUserName=userName)
           # itchat.send('%s'%(strkey),toUserName=userName)





if __name__ == '__main__':
    itchat.auto_login()#enableCmdQR=True 可以在命令行显示二维码
    itchat.run()
