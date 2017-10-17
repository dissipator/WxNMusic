# 树莓派版网易云音乐播放器

注意，该版本为树莓派版，如果需要使用电脑版(Windows/Linux/OSX)，[请点击这里](https://github.com/yaphone/WxNeteaseMusic)。

## 来源

之前毕业的时候实在闲的无聊，正好手头上有个树莓派，就写了个简单的网易云音乐播放器，代码很简单，写的也很乱，功能更简单--只能搜索歌曲，然后播放之，放在了github上，没想到竟然收到三十多颗星，实在惭愧，然后放年假，就想着把功能稍微完善一下，于是就有了[WxNeteaseMusic](https://github.com/yaphone/RasWxNeteaseMusic)，其实做的工作也不多，基于[itchat](https://github.com/littlecodersh/ItChat)和[网易云音乐的python API](https://github.com/yaphone/musicbox)，废话不多说，容我简单介绍一下吧。

首先，我的场景是这样的，实验室是有一台电脑放音乐的，大家切歌就要跑到那里操作，比较麻烦，后来我就想做个后台，用微信来操作切歌这些，这样大家只要加了我的微信号，发相关指令就可以了，还是比较方便的。再后来，电脑换成了树莓派，我就又移植到了树莓派上。不过这里吐槽一下，树莓派的原生音质确实渣，我们后来买了个 DAC ，完美。😁

## 安装

项目源码都都在[我的Github](https://github.com/yaphone/RasWxNeteaseMusic)上，大家先下载下来，麻烦大家顺手点个star哟~，谢谢。
我们以树莓派环境为例，安装其实很简单，都是一些python的pip依赖包:

- sudo apt-get install python-dev
- sudo pip install requests
- sudo pip install future
- sudo pip install crypto 
- sudo pip install bs4 
- sudo pip install pycrypto
- sudo pip install itchat

上面这些依赖应该够了，如果提示缺少包的话，大家根据提示自行安装就可以了，切换到RasWxNeteaseMusic目录，执行python run.py 
用微信扫码登陆，Bingo, just enjoy it !

## 功能
嗯，先来看看都有什么功能。

- H: 帮助信息
- L: 登陆网易云音乐
- U: 用户歌单
- M: 播放列表
- N: 下一曲
- R: 正在播放
- S: 歌曲搜索
- T: 热门单曲
- E: 退出

这就是RasWxNeteaseMusic V0.1版的功能菜单啦，后面如果大家有其它的需求或者使用过程中有什么问题，都可以提出来，github上提Issue或者在下面评论都可以，后面我会尽量完善。

## 使用

微信扫码登陆后，向登陆的微信号发送命令，就可以使用了。我的微信号是可以自己向自己发送信息的，使用起来比较方便，但是有些微信号好像不能自己给自己发信息，这种情况下，就需要通过另一个微信号向扫码登陆的微信号发命令。这里需要注意，扫码的时候itchat是以网页版/电脑版的方式登陆微信的，如果扫码的手机退出微信客户端，那么WxNeteaseMusic自然也不能正常使用。不过也有手机退出微信但是网页版/电脑版不退出的办法，大家自行百度一下。
如果大家看一下代码就会发现，WxNeteaseMusic是以空格为分隔符来切割命令的，所以对于有两个或者三个参数的命令时，需要以空格为分隔符，下面我具体来介绍一下。

### 获取帮助信息

发送 `H`。

### 登陆网易云音乐

命令格式为 `L 用户名 密码`，注意，`L`和`用户名`、`密码`之间以空格分开，这里的用户名和密码是你的网易云音乐的用户名和密码，邮箱格式。之后客户端会收到一条消息，登陆成功或者登陆失败，如果登陆成功，WxNeteaseMusic会保存你的UserId，所以并不需要每次使用都要登陆账号，除非要换其它账号，UserId在网易云音乐中是唯一的，用户的歌单、收藏列表等信息都是通过UserId来获取的。登陆成功后，就可以使用下面的功能了，默认是我的UserId哦，别忘记登录呀~

### 获取用户歌单

登陆成功后，播放列表默认为网易云音乐的热歌榜，些时发送`U`可以获取用户的歌单，就是你在网易云音乐创建的歌单，获取歌单后，通过命令`U 序号`来选择对应的歌单，注意`U`和`序号`之间有空格，此时播放列表是你歌单里的歌曲。

### 播放列表

使用过程中，发送`M`可以随时查看当时的播放列表。

### 下一曲

发送命令`N`来播放下一曲，`N 序号`播放列表中对应的歌曲，当前列表通过命令`M`获取。这里需要注意，通过`N 序号`选择列表中的歌曲时，播放是临时的，并不保存在播放列表中，此时再发`R`命令时显示的播放信息是错误的。

### 正在播放

发送命令`R`可获取正在播放的歌曲详情。

### 歌曲搜索

发送命令`S 歌曲名`可进行歌曲搜索，成功后会返回搜索结果列表，再发送`S 歌曲名 序号`来播放对应序号的歌曲，注意，两次命令的歌曲名必须完全一致。

### 热门单曲榜

发送`T`获取网易云音乐的热门单曲榜，并更新播放列表。

### 退出

发送`E`退出播放，此时播放列表变为空，用户如果要恢复播放，需要获取歌单更新播放列表。

## 功能演示

好吧好吧，说了这么多，还是让我来实际来演示一下吧。注意，演示中的登陆密码我已经修改了，你们就不要试了哈。

![演示](http://oj5vdtyuu.bkt.clouddn.com/wxneteasemusic1.gif)

如果还不清楚的话，我还拍了个小视频，放在了优酷上，[请点击这里](http://v.youku.com/v_show/id_XMjUxODk5MDQxNg==.html)。

[![视频演示](http://oj5vdtyuu.bkt.clouddn.com/screenshot.png)](http://v.youku.com/v_show/id_XMjUxODk5MDQxNg==.html?tpa=dW5pb25faWQ9MTAzMjUyXzEwMDAwMV8wMV8wMQ+)

### Todo List

- 增加控制音量功能 `amixer sset PCM 80%`

## 其它

当前在树莓派上使用的播放器为raspbian自带的omxplayer，因为python的mp3play包不能在树莓派上使用，后来对比了mpg123和omxplayer发现，omxplayer音质还要相对好一些。另外，在登陆网易云音乐的时候需要进行一个加密算法，由于树莓派的计算能力有限，所以需要多等待一会。

## BUGS

1.网易云音乐中部分音乐链接已失效，所以可能导致播放失败的情况，这种情况下，因为树莓派版使用的是omxplayer，而非[其它平台下的WxNeteaseMusic](https://github.com/yaphone/WxNeteaseMusic)使用的mp3play模块，omxplayer并不能感知到播放失败，还会一直等待当前播放失败的歌曲的时长才会播放下一首，或者其它命令触发切换动作，如（N）等，建议使用网易音乐的客户端把播放失败的这首歌直接删除掉，这样在树莓派上播放时就不会卡住了。而电脑版使用的是python的mp3play包，播放失败时会自动跳过。

2.通过`N 序号`选择列表中的歌曲时，播放是临时的，并不保存在播放列表中，此时再发`R`命令时显示的播放信息是错误的。

3.如果出现二维码不完整的问题，是linux平台编码字符宽度问题，尝试使用itchat.auto_login(enableCmdQR=True)。












