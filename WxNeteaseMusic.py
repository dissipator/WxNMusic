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
        self.new_url = None
        self.mpd = self.mpd_init()
        self.player = {
            "playing" : False,
            "stop" : True,
            "pause" : False,
            "status" : None
        }
        #volume: 95%   repeat: off   random: off   single: off   consume: off
        self.playTime = int(self.song.get('playTime'))//1000
        self.mp3 = None
        t = threading.Thread(name="t",target=self.play)
        t.start()

    def mpd_init(self):
        print("mpd_init")
        mpd = True
        mpds = int(os.popen('ps -ef | grep -v grep | grep mpd| wc -l').read())
        if mpds >1:
            mpd = False
        while mpd:
            print("restart mpd")
            s = os.popen("sudo systemctl restart mpd.socket", 'w').write('\n')
            time.sleep(5)
            s = os.popen("sudo systemctl start mpd.socket", 'w').write('\n')
            os.popen("mpc play")
            mpds = int(os.popen('ps -ef | grep -v grep | grep mpd| wc -l').read())
            if mpds >1:
                mpd = False
        print("mpd is areadly!")
        return True

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
        if len(self.playlist) > 0:
            print('recived N index :',self.song_index)
            self.song_index = self.song_index + 1
            print('new index:  ',self.song_index)
            index = self.song_index
            song = self.playlist[index]
            mpc = str(os.popen('mpc next').read())
            mpc = str(os.popen('mpc play').read())
            res = u'切换成功，正在播放: song_index: ' + str(self.song_index) +song.get('song_name')
        return res

    def next_by_index(self,index):
        next_index = self.song_index + 2
        tmp_song = self.playlist[index]
        self.playlist.insert(next_index, tmp_song)
        print(self.playlist[index],self.playlist[next_index])
        self.load_url(next_index,tmp_song)
        os.popen('mpc play %d' % next_index)
        self.song_index = next_index
        del self.playlist[-1]

    def prev(self):
        self.song_index -= 1
        mpc = str(os.popen('mpc prev').read())

    def mpd_status(self):
        #volume: 95%   repeat: off   random: off   single: off   consume: off
        mpc = os.popen('mpc ').read().split()
        # print("mpd_status",mpc)
        status = ''
        while not self.mpd:
            self.mpd = self.mpd_init()

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

        if self.player['stop']:
            status = self.format_mpc(mpc,"stop")
        else:
            status = self.format_mpc(mpc,"playing")
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
        # print(strs)
        if way in ['','status','stop']:
            for i in range(0,len(strs)):
                key = strs[i].split(':')
                if key[0] in (lists):
                    # print(key[0],strs[i+1])
                    status[key[0]] = strs[i+1]
        elif way in ['play','playing']:
            status['name'] = strs[0]
            n,status['index'],status['totle'] = re.split('#|/',strs[2])
            self.song_index = status['index']
            status['timeing'],status['song_time'] = re.split('/',strs[3])
            status['prest'] = strs[4]
            for i in range(5,len(strs)):
                key = strs[i].split(':')
                if key[0] in (lists):
                    status[key[0]] = strs[i+1]
        # print(status)
        return status

    def send_msg(self,res):
        itchat.send(res, "filehelper")

    def t_fromat(self,song_time):
        song_time ="%s:%s" %( song_time//60,song_time%60) 
        return song_time
    def load_url(self,index=0, song=''):
        print("load_url")
        if song == '':
            song = self.playlist[self.song_index]
        song_id = song["song_id"]
        try:
            mp3_url = song["mp3_url"]
            new_url = MyNetease().songs_detail_new_api([song_id])[0]['url']
            self.playlist[self.song_index]['new_url'] = new_url
            song['new_url'] = new_url
            print("add url : ",new_url)
            os.popen('mpc add ' + new_url)
        except Exception as e:
            print(e)
            # os.popen('mpc add ' + mp3_url)
        # print(os.popen('mpc playlist '))
        return song

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
                    res = self.next()
                    if self.con.acquire():
                        self.con.notifyAll()
                        self.con.release()
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
                os.popen('mpc clear')
                self.song_index = 0
                self.load_url()
                self.play()               
                res += u'\n回复 (N) 播放下一曲， 回复 (N 序号)播放对应歌曲'
            elif arg == u'G':#推荐歌单
                self.playlist = self.myNetease.get_recommend_playlist()
                if len(self.playlist) == 0:
                    res = u"当前播放列表为空，请回复 (U) 选择播放列表"
                i = 0
                for song in self.playlist:
                    res += str(i) + ". " + song["song_name"] + "\n"
                    i += 1
                os.popen('mpc clear')
                self.song_index = 0
                self.load_url()
                self.play()
                res += u'\n回复 (N) 播放下一曲， 回复 (N 序号)播放对应歌曲'
            elif arg in [u"mpd", u"Mpd", u"MPD"]:
                res = u"回复: " + str(self.mpd_status())
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
                        self.song_index = 0
                        os.popen('mpc clear')
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
                # self.playlist.insert(0, tmp_song)
                res = self.next_by_index(index)
                if self.con.acquire():
                    self.con.notifyAll()
                    self.con.release()
                time.sleep(.5)
                # del self.playlist[-1]

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
   
    def print_ststus(self,count):
        song = self.song
        p = "playing : \nsongs : %d \n index: %d \n song : %s" % (count, self.song_index,song["song_name"])
        print(p)
        self.send_msg(str(p))
        # for s in self.song:
            # print(s,self.song[s])
        p = self.mpd_status()

    def play(self,next_time=0):
        os.popen('mpc clear')
        self.load_url()
        self.play()
        index = 0
        while True:
            time.sleep(1)
            if self.con.acquire():
                if len(self.playlist) != 0:
                    p_index = self.song_index
                    status = self.mpd_status()
                    if p_index == index:
                        index = int(self.song_index) + 1
                    else:
                        index = index + 1
                    print(p_index,self.song_index,index)
                    # print("load next song url : %d" % index )
                    next_song = self.playlist[index]
                    next_song_name = next_song["song_name"]
                    # print(next_song)
                    next_time = int(next_song.get('playTime'))/1000 - 10
                    self.load_url(index,next_song)
                    msg = "Next song is : %s " % ( next_song_name )
                    self.send_msg(msg)
                    self.con.notifyAll()
                    self.con.wait(20)
                try:
                    pass
                except Exception as e:
                    raise e