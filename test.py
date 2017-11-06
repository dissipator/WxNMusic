#!/usr/bin/env python
#encoding: UTF-8

import hashlib
from neteaseApi import api

class MyNetease:
    def __init__(self):
        self.netease = api.NetEase()
        self.userId = int(open("./userInfo", 'r').read())
        # self.login('13666244245','lou8i7u9k')


    def login(self, username, password): #用户登陆
        password = hashlib.md5(password.encode('utf-8')).hexdigest()
        login_info = self.netease.login(username, password)
        if login_info['code'] == 200:
            res = u"登陆成功"
            #登陆成功保存userId，作为获取用户歌单的依据，userId是唯一的，只要登陆成功，就会保存在userInfo文件中，所以不必每次都登陆
            userId = login_info.get('profile').get('userId')
            self.userId = userId
            file = open("./userInfo", 'w')
            file.write(str(userId))
            file.close()
            file.close()
            file = open("./logInfo", 'w')
            file.write(str(login_info))
            file.close()

        else:
            res = u"登陆失败"
        return res

    def songs_detail_new_api(self, music_ids):
        data = self.netease.songs_detail_new_api(music_ids)
        return data

from http.cookiejar import LWPCookieJar
api = api.NetEase()
api.session.cookies = LWPCookieJar(api.storage.cookie_path)


Cookie = "<Cookie MUSIC_U=8b6953ca49c6ec854f7c79e7604efb997797a480fd964d1e6cfc9fe107745c541a21e41892ef7e03e8e42c3d72bc6e818b33f02b35155df18b4339f007aa4526f2d065378fd669ad846c26372a8b4a41 for music.163.com/>, <Cookie __csrf=8debf7cc3e19c65e09b73810ed371730 for music.163.com/>, <Cookie __remember_me=true for music.163.com/>"

if __name__ == '__main__':
        # netease = api.NetEase()
        # userId = int(open("./userInfo", 'r').read())
        # password = hashlib.md5("lou8i7u9k".encode('utf-8')).hexdigest()
        # log = netease.login('13666244245', password)
        # netease.songs_detail_new_api(515803379)
        # print(log)
        MyNetease =  MyNetease()
        # MyNetease.login('13666244245','lou8i7u9k')
        print(MyNetease)
        MyNetease.songs_detail_new_api(515803379)

# from myapi import MyNetease

# netease = MyNetease()
# print (netease.login("zhouyaphone@163.com", "a123456"))

# import sys
# from subprocess import PIPE, Popen
# from threading  import Thread

# mp3_url =  netease.songs_detail_new_api(515803379)


# try:
#     from Queue import Queue, Empty
# except ImportError:
#     from queue import Queue, Empty  # python 3.x

# ON_POSIX = 'posix' in sys.builtin_module_names

# def enqueue_output(out, queue):
#     for line in iter(out.readline, b''):
#         queue.put(line)
#     out.close()

# # p = Popen("omxplayer " + mp3_url, shell=True, stdout=PIPE, bufsize=1, close_fds=ON_POSIX)
# p = Popen("mpc play " + mp3_url, shell=True, stdout=PIPE, bufsize=1, close_fds=ON_POSIX)
# q = Queue()
# t = Thread(target=enqueue_output, args=(p.stdout, q))
# t.daemon = True # thread dies with the program
# t.start()

# # ... do other things here

# # read line without blocking
# try:
#     line = q.get_nowait() # or q.get(timeout=.1)
#     # line = q.get(timeout=3)
# except :
#     print('no output yet')
# else: # got line
#     if "nice" in line:
#         print ("*******OK*******")
