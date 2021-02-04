# ffmpeg 笔记

家有 NAS，那肯定就会遇到影音相关的问题。

## 视频转码

最近买了一个 VR 设备：Oculus Quest 2，想用它看 NAS 中的视频，但是又不想付费购买 Skybox 之类的软件。
因此就在鼓捣如何通过浏览器直接观看 NAS 视频。

首先排除掉 jellyfin，在树梅派4B上装了这东西结果卡得不行，用不了。

于是使用 caddy 直接搭了个静态文件服务器，现在 mp4 视频能直接用浏览器播放了，可是 mkv 不行。。。

现在进入文章重点：如何使用 ffmpeg 进行视频转码。

mkv 转 mp4:

```shell
# 直接复制所有内容
# -c copy 同时设定 video/audio 的编码器(encoder)为 copy
# -c:s mov_text 字幕也直接复制（mp4 的独立字幕，部分播放器可能不支持）
ffmpeg -i "input.mkv" -c copy -c:s mov_text "output.mp4"

# 批量转格式，直接复制内容
for $item in `find . -name "*.mkv"` do ffmpeg -i "$item" -c copy "$item.mp4"

# 重新使用 h265 进行编码（目前浏览器基本都不支持 h265）
# -c:a copy 音频直接拷贝
# -c:v libx264 视频使用 x264 重新编码
# -c:s mov_text 字幕也直接复制（mp4 的独立字幕，部分播放器可能不支持）
# -b:v 6M  视频码率，1080p/24fps 推荐 5M-12M，10M 的话大概 14 分钟 1G 空间。
# -crf 是质量参数，建议值设在 18-28 之间（越小越接近无损，默认 23）
ffmpeg -i "xxx.mkv" -c:a copy -c:s mov_text -c:v libx264 "xxx.mp4"
```

flv 等其他视频的互相转换，也是使用同样的命令。

编码的详细参数参见 [不同编码器特有的设定](https://gloomy-ghost.gitbooks.io/-ffmpeg/content/08-differente-encoders-special-options.html#%E5%AD%A6%E4%BC%9A%E7%9C%8B%E6%96%87%E6%A1%A3)




## 其他奇技淫巧

查看视频信息：

```shell
ffprobe -i "xxx.mkv"
```

视频截取：

视频转 gif 图:


## GPU 加速

ffmpeg 默认使用 cpu，因为它最通用。但是编解码时 CPU 跑满不说，速度也慢。

其实 ffmpeg 也支持在部分硬件上启用硬件加速功能，下面以 Nvidia 显卡为例做介绍。

对 manjaro(arch) linux 系统，首先安装环境：

```shell
sudo pacman -S ffmpeg cuda
```

使用 cuda 加速编码：

```shell
ffmpeg -vsync 0 -hwaccel cuda -hwaccel_output_format cuda -i input.mkv -c:a copy -c:v h264_nvenc -b:v 6M output.mp4
```

我测试发现 8bits 的视频都能正常转码，但是 10bits 的会报错 `[h264_nvenc @ 0x559ae50d5540] 10 bit encode not supported`.
网上搜索说要加个过滤器把 10bits 转成 8bits 才能进行加速，还未解决。

另外我有看到加速有的人选用 `cuvid` 而不是 cuda，这个目前还不是很清楚。


## 学习资料

- [digital_video_introduction](https://github.com/leandromoreira/digital_video_introduction)
- [ffmpeg-libav-tutorial](https://github.com/leandromoreira/ffmpeg-libav-tutorial)
