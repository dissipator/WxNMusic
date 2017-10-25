#!/usr/bin/env python
# encoding: UTF-8
'''
网易云音乐 Entry
'''



from WxNeteaseMusic import WxNeteaseMusic
import itchat
from itchat.content import *
wnm = WxNeteaseMusic()

@itchat.msg_register(itchat.content.TEXT)
def mp3_player(msg):
    text = msg['Text']
    res = wnm.msg_handler(text)
    # itchat.send(text,"filehelper")
    itchat.send(res, 'filehelper')
    # itchat.send(res)  
    return res

itchat.auto_login(hotReload=True,enableCmdQR=True)
itchat.run(debug=True)
