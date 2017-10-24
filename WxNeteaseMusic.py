#coding=utf-8
import itchat
import re
import threading
import time
import subprocess
from myapi import MyNetease
import os
class WxNeteaseMusic:
    def __init__(self):
        self.help_msg = \
            u"H: 帮助信息\n" \
            u"L: 登陆网易云音乐\n" \
            u"M: 播放列表\n" \
            u"N: 下一曲\n"\
            u"U: 用户歌单\n"\
            u"R: 正在播放\n"\
            u"S: 歌曲搜索\n"\
            u"T: 热门单曲\n"\
            u"G: 推荐单曲\n"\
            u"E: 退出\n"
        self.con = threading.Condition()
        self.myNetease = MyNetease()
        self.playlist = self.myNetease.get_top_songlist()  #默认是热门歌单
        self.song_index = 0
        self.song =self.playlist[self.song_index]
        self.song_id = self.song["song_id"]
        self.new_url = MyNetease().songs_detail_new_api([self.song_id])[0]['url']
        self.player = {
            "song_index" : self.song_index,
            "playing" : False,
            "stop" : True,
            "pause" : False,
            "song" : self.song,
            "new_url" : self.new_url,
            "status" : None
        }
        #volume: 95%   repeat: off   random: off   single: off   consume: off
        self.playTime = int(self.song.get('playTime'))//1000
        self.mpd = self.mpd_init()
        self.mp3 = None
        t = threading.Thread(target=self.play)
        t.start()

    def mpd_init(self):
        print("mpd_init")
        mpd = int(os.popen('ps -ef | grep -v grep | grep mpd| wc -l').read())
        time.sleep(1)
        while mpd < 1 :
            print("restart mpd")
            s = os.popen("sudo pkill -9 mpd", 'w').write('\n')
            time.sleep(1)
            s = os.popen("sudo service mpd start", 'w').write('\n')
            mpd = int(os.popen('ps -ef | grep -v grep | grep mpd| wc -l').read())
        print("mpd is areadly!")
        self.mpd = True

    def do_play(self):
        print("paly")
        try:
            mpc = str(os.popen('mpc play').read())
        except Exception as e:
            self.mpd_init()
            mpc = str(os.popen('mpc play').read())
        self.playing = True
        self.play_stop = False
        self.play_pause = False

    def pause(self):
        mpc = str(os.popen('mpc pause').read())
        self.playing = False
        self.play_stop = False
        self.play_pause = True

    def stop(self):
        mpc = str(os.popen('mpc stop').read())
        self.playing = False
        self.play_stop = True
        self.play_pause = False

    def next(self):
        mpc = str(os.popen('mpc next').read())
        self.song_index += 1
    def next_by_index(self,index):
        mpc = str(os.popen('mpc play %s' % index ).read())

    def prev(self):
        mpc = str(os.popen('mpc prev').read())
        self.song_index -= 1

    def mpd_status(self):
        #volume: 95%   repeat: off   random: off   single: off   consume: off
        mpc = os.popen('mpc ').read().split()
        print("mpd_status",mpc)
        if mpc[1] == "[playing]":
            self.player['playing'] = True
            self.player['stop'] = False
            self.player['pause'] = False
        elif mpc[1] == "[paused]":
            self.player['playing'] = False
            self.player['stop'] = False
            self.player['pause'] = True
        else:
            self.player['playing'] = False
            self.player['stop'] = True
            self.player['pause'] = False

        if not self.player['stop']:
            status = self.format_mpc(mpc,"stop")
        return status

    def mpd_mode(self,mode=''):
        if mode == '':
            print('mode error')
        else:
            mpc = 'mpc %s' % mode
            strs = os.popen(mpc).read()
            remode = self.mpd_status()
            return remode[mode]
        #repeat: off   random: off   single: off   consume: off

    def format_mpc(self,strs,way):
        lists = ["volume","repeat","random","single","consume"]
        status = {}
        if way in ['','status','stop']:
            for i in range(0,len(strs)):
                key = strs[i].split(':')
                if key[0] in (lists):
                    print(key[0],strs[i+1])
                    status[key[0]] = strs[i+1]
        elif way in ['play','playing']:
            status['name'] = strs[0]
            if strs[1]=='[playing]':
                self.player['playing'] = True
                self.player['stop'] = False
                self.player['pause'] = False
            else:
                self.player['playing'] = True
                self.player['stop'] = False
                self.player['pause'] = False
            n,self.song_index,status['totle'] = re.split('#|/',strs[2])
            status['timeing'],status['song_time'] = re.split('/',strs[3])
            status['prest'] = strs[4]
            for i in range(5,len(strs)):
                key = strs[i].split(':')
                if key[0] in (lists):
                    print(key[0],strs[i+1])
                    status[key[0]] = strs[i+1]
        return status

    def send_msg(self,res):
        itchat.send(res, "filehelper")

    def t_fromat(self,song_time):
        song_time ="%s:%s" %( song_time//60,song_time%60) 
        return song_time

    def load_playlist(self):
        print("load_playlist")
        playlist = self.playlist
        os.popen('mpc clear ')
        self.do_play()
        for song in playlist:
            song_id = song["song_id"]
            mp3_url = song["mp3_url"]
            new_url = MyNetease().songs_detail_new_api([song_id])[0]['url']
            # print('add',new_url)
            try:
                # shell = subprocess.Popen('mpc add ' + new_url, 
                    # shell=True, stdout=subprocess.PIPE)
                # shell.run()
                os.popen('mpc add ' + new_url)
            except:

                # subprocess.Popen('mpc add ' + new_url,
                         # shell=True, stdout=subprocess.PIPE)
                # shell.run()
                os.popen('mpc add ' + mp3_url)
 
    def msg_handler(self, args):
        arg_list = args.split(" ")  # 参数以空格为分割符
        res = ''
        if len(arg_list) == 1:  # 如果接收长度为1
            arg = arg_list[0]
            res = ""
            if arg in [u'H',u'h']:  # 帮助信息
                res = self.help_msg
            elif arg in [u'p',u'P']:  # 下一曲
                self.do_play()
            elif arg in [u'N',u'n']:  # 下一曲
                if len(self.playlist) > 0:
                    if self.con.acquire():
                        self.con.notifyAll()
                        self.con.release()
                    self.next()
                    res = u'切换成功，正在播放: ' +self. playlist[0].get('song_name')
                else:
                    res = u'当前播放列表为空'
            elif arg == u'U':  # 用户歌单
                user_playlist = self.myNetease.get_user_playlist()
                if user_playlist == -1:
                    res = u"用户播放列表为空"
                else:
                    index = 0
                    for data in user_playlist:
                        res += str(index) + ". " + data['name'] + "\n"
                        index += 1
                    res += u"\n 回复 (U 序号) 切换歌单"
            elif arg == u'M': #当前歌单播放列表
                if len(self.playlist) == 0:
                    res = u"当前播放列表为空，回复 (U) 选择播放列表"
                i = 0
                for song in self.playlist:
                    res += str(i) + ". " + song["song_name"] + "\n"
                    i += 1
                res += u'\n回复 (N) 播放下一曲， 回复 (N 序号)播放对应歌曲'
            elif arg in [u'R',u"r"]: #当前正在播放的歌曲信息
                song_info = self.playlist[-1]
                song_id= song_info.get("song_id")
                artist = song_info.get("artist")
                song_name = song_info.get("song_name")
                album_name = song_info.get("album_name")
                new_url = MyNetease().songs_detail_new_api([song_id])[0]['url']
                res = u"歌曲：" + song_name + u"\n歌手：" + artist + u"\n专辑：" + album_name
            elif arg == u"S": #单曲搜索
                res = u"回复 (S 歌曲名) 进行搜索"
            elif arg == u'T': #热门单曲
                self.playlist = self.myNetease.get_top_songlist()
                if len(self.playlist) == 0:
                    res = u"当前播放列表为空，请回复 (U) 选择播放列表"
                i = 0
                for song in self.playlist:
                    res += str(i) + ". " + song["song_name"] + "\n"
                    i += 1
                load_list = threading.Thread(target=self.load_playlist,stdout=subprocess.PIPE)
                load_list.start()                
                res += u'\n回复 (N) 播放下一曲， 回复 (N 序号)播放对应歌曲'
            elif arg == u'G':#推荐歌单
                self.playlist = self.myNetease.get_recommend_playlist()
                if len(self.playlist) == 0:
                    res = u"当前播放列表为空，请回复 (U) 选择播放列表"
                i = 0
                for song in self.playlist:
                    res += str(i) + ". " + song["song_name"] + "\n"
                    i += 1
                load_list = threading.Thread(target=self.load_playlist,stdout=subprocess.PIPE)
                load_list.start()
                res += u'\n回复 (N) 播放下一曲， 回复 (N 序号)播放对应歌曲'
            elif arg in [u'E',u'e']:#关闭音乐
                self.playlist = []
                subprocess.Popen("mpc stop" , shell=True, stdout=subprocess.PIPE)
                if self.con.acquire():
                    self.con.notifyAll()
                    self.con.release()
                    res = u'播放已退出，回复 (U) 更新列表后可恢复播放'
            else:
                res = self.mpd_status()
                try:
                    index = int(arg)
                    if index > len(self.playlist) - 1:
                        res = self.mpd_status()
                        # res = u"这是来自机器人的回复！"
                    else:
                        if self.con.acquire():
                            self.con.notifyAll()
                            self.con.release()
                except:
                    res = self.mpd_status()
                    # res = u'这是来自机器人的回复！'

        elif len(arg_list) == 2:  #接收信息长度为2
            arg1 = arg_list[0]
            arg2 = arg_list[1]
            if arg1 in [u"u",u"U"]:
                user_playlist = self.myNetease.get_user_playlist()
                if user_playlist == -1:
                    res = u"用户播放列表为空"
                else:
                    try:
                        index = int(arg2)
                        data = user_playlist[index]
                        playlist_id = data['id']   #歌单序号
                        song_list = self.myNetease.get_song_list_by_playlist_id(playlist_id)
                        self.playlist = song_list
                        print(song_list)
                        load_list = threading.Thread(target=self.load_playlist)
                        load_list.start()
                        res = u"用户歌单切换成功，回复 (M) 可查看当前播放列表"
                        self.do_play()
                        if self.con.acquire():
                            self.con.notifyAll()
                            self.con.release()
                    except:
                        res = u"输入有误"
            elif arg1 in [u'n', u'N']: #播放第X首歌曲
                index = int(arg2)
                tmp_song = self.playlist[index]
                self.playlist.insert(0, tmp_song)
                self.next_index(index)
                if self.con.acquire():
                    self.con.notifyAll()
                    self.con.release()
                self.playTime = int(self.playlist[0].get('playTime'))/1000/60
                self.next_by_index(index)
                res = u'切换成功，正在播放: %s ,时长：%s' % (self.playlist[0].get('song_name'),self.playTime)
                time.sleep(.5)
                del self.playlist[-1]

            elif arg1 == u"S": #歌曲搜索+歌曲名
                song_name = arg2
                song_list = self.myNetease.search_by_name(song_name)
                res = ""
                i = 0
                for song in song_list:
                    res += str(i) + ". " + song["song_name"] + "\n"
                    i += 1
                res += u"\n回复（S 歌曲名 序号）播放对应歌曲"
            elif arg1 in [u"cmd", u"CMD"]:
                try:
                    res = str(os.popen(arg2).read())
                except :
                    res = self.mpd_status()

        elif len(arg_list) >= 3:   #接收长度为3
            arg1 = arg_list[0]
            arg2 = arg_list[1]
            arg3 = arg_list[2]
            try:
                if arg1 == u'L':  #用户登陆
                    username = arg2
                    password = arg3
                    res = self.myNetease.login(username, password)
                elif arg1 == u"S":
                    song_name = arg2
                    song_list = self.myNetease.search_by_name(song_name)
                    index = int(arg3)
                    song = song_list[index]
                    #把song放在播放列表的第一位置，唤醒播放线程，立即播放
                    self.playlist.insert(0, song)
                    if self.con.acquire():
                        self.con.notifyAll()
                        self.con.release()
                    artist = song.get("artist")
                    song_name = song.get("song_name")
                    album_name = song.get("album_name")
                    res = u"歌曲：" + song_name + u"\n歌手：" + artist + u"\n专辑：" + album_name
                elif arg1 in [u"CMD",u"cmd"]:
                    cmd = ''
                    for i in range(1,len(arg_list)):
                        if i>0 :
                            cmd += arg_list[i]+" "
                    print("cmd : " + cmd)
                    try:
                        res = str(os.popen(cmd).read())
                        # self.send_msg(res)
                    except Exception as res:
                        raise res
                else:
                    res = self.mpd_status()
            except:
                res = self.mpd_status()
        return res

    def play(self):
        self.mpd_status()
        # load_list = threading.Thread(target=self.load_playlist)
        # load_list.start()
        while True:
            time.sleep(1)
            # print(self.player["song_index"])
            if self.con.acquire():
                if len(self.playlist) != 0:
                    try:
                        self.send_msg(self.mpd_status())
                        print(self.song_index)
                    except Exception as e:
                        print(e)
                        self.mpd_init()
                        self.do_play()
                self.con.notifyAll()
                self.con.wait(self.playTime)
                
    def play2(self):
        while True:
            if self.con.acquire():
                if len(self.playlist) != 0:
                    # 循环播放，取出第一首歌曲，放在最后的位置，类似一个循环队列
                    song = self.playlist[0]
                    song_id = song["song_id"]
                    mp3_url = song["mp3_url"]
                    new_url = MyNetease().songs_detail_new_api([song_id])[0]['url']
                    self.playTime = int(song.get('playTime'))//1000+3
                    print(mpd)
                    while mpd < 1 :
                        # os.popen("sudo make install", 'w').write('momlku')
                        print("restart mpd")
                        s = os.popen("sudo pkill -9 mpd", 'w').write('\n')
                        time.sleep(5)
                        s = os.popen("sudo service mpd start", 'w').write('\n')
                        # subprocess.Popen("sudo service mpd start" , shell=True,
                        #                  stdout=subprocess.PIPE)
                        mpd = int(os.popen('ps -ef | grep -v grep | grep mpd| wc -l').read())
                    print("mpd is areadly!")
                    
                    try:
                        # subprocess.Popen("pkill omxplayer", shell=True)
                        time.sleep(1)
                        os.popen('mpc add ' + new_url)
                        time.sleep(1)
                        os.popen('mpc next')
                        print("play")
                        playing = str(os.popen('mpc play').read())                 
                        res = u'切换成功，正在播放: %s,时长：%s ' % (song["song_name"],self.t_fromat(self.playTime))
                        self.send_msg(res)
                        self.send_msg(playing)
                        # time.sleep(self.playTime)
                        self.con.notifyAll()
                        self.con.wait(self.playTime)
                    except:
                        os.popen('mpc add ' + mp3_url)
                        time.sleep(1)
                        os.popen('mpc next')
                        print("play")
                        playing = str(os.popen('mpc play').read())
                        res = u'切换成功，正在播放:%s,时长:%s ' % (song["song_name"],self.t_fromat(self.playTime))
                        self.send_msg(res)
                        self.send_msg(playing)
                        self.con.notifyAll()
                        self.con.wait(self.playTime)
                    finally:
                        pass
                else:
                    try:
                        # subprocess.Popen("pkill omxplayer", shell=True)
                        stop = str(os.popen('mpc stop').read())
                        print(stop)
                        self.con.notifyAll()
                        self.con.wait()
                    except:
                        pass

