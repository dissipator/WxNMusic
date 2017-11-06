#!/usr/bin/env python
# encoding: UTF-8
'''
网易云音乐 Entry
'''



from WxNeteaseMusic import WxNeteaseMusic
import itchat
from itchat.content import *
easygui = False
try:
    import easygui
    from  easygui import *
    easygui = True
except :
    pass

wnm = WxNeteaseMusic()


# @itchat.msg_register(itchat.content.TEXT)
# def mp3_player(msg):
#     text = msg['Text']
#     res = wnm.msg_handler(text)
#     # itchat.send(text,"filehelper")
#     itchat.send(res, 'filehelper')
#     # itchat.send(res)  
#     return res

@itchat.msg_register(TEXT)
def text_reply(msg):    
    text = msg['Text']
    friends = itchat.search_friends(userName=msg["FromUserName"])['NickName']
    title = "From: %s" % friends
    fieldNames = ["消息来自:","消息：","回复："]
    fieldValues = [friends,text]  # we start with blanks for the values

    res = wnm.msg_handler(text)
    # itchat.send(text,"filehelper")
    # itchat.send(res, 'filehelper')
    if res:
        return res
    else:
        try:
            req = multenterbox(title, title, fieldNames,fieldValues)
            if len(req[2])>0 and req != '':
            #itchat.send(req[2], friends)
                return req[2]
        except :
            pass



itchat.auto_login(hotReload=True,enableCmdQR=False)
itchat.run(debug=True)
