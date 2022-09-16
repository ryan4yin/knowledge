# ffmpeg 笔记

家有 NAS，那肯定就会遇到影音相关的问题。


## 图片处理

将任何格式的静态图片压缩并转换为 webp:

```shell
ffmpeg -i input.png  -vf scale=iw:ih -codec libwebp -lossless 0 -quality 75 out.webp

# 转换格式的同时进行图片放缩
ffmpeg -i input.png -c:v libwebp -vf scale=2000:-1 out.webp
```

注：

- 对于 png 格式的原图，选择无损压缩时，`-lossless -quality 100` 是最佳方案。其他格式不建议使用此参数。
- 选择有损压缩时，`-quality 75` 是最佳方案

## 视频处理

### 简单用法

查看视频信息：

```shell
ffprobe -i "xxx.mkv"
```

### 视频转码

最近买了一个 VR 设备：Oculus Quest 2，想用它看 NAS 中的视频，但是又不想付费购买 Skybox 之类的软件。
因此就在鼓捣如何通过浏览器直接观看 NAS 视频。

首先排除掉 jellyfin，在树梅派4B上装了这东西结果卡得不行，用不了。

于是使用 caddy 直接搭了个静态文件服务器，现在 mp4 视频能直接用浏览器播放了，可是 mkv 不行。。。

现在进入文章重点：如何使用 ffmpeg 进行视频转码。

gif 与 mp4 的互转：

```shell
# gif 转 mp4/flv 并同时进行压缩

# 通过降低帧率与码率来压缩视频
# -r 15        将帧率调整为 15
# -b:v 1M      将码率调整为 1M
ffmpeg -i input.gif -r 15 -b:v 1M output.mp4

# 通过重编码来压缩视频
# -preset veryslow 以极慢的速率进行编码，得到的视频质量当然会是最好的，不过代码就是时间
# -crf             是质量参数，建议值设在 18-28 之间（越小越接近无损，默认 23）建议自己多测测，看看效果
ffmpeg -i input.gif -preset veryslow -r 20 -crf 18 -b:v 1M output.mp4
# 再进一步转为 flv（发现 gif 直接转 flv 画质会变得惨不忍睹，需要用 mp4 作为中转）
ffmpeg -i "input.mp4" -c copy -c:s mov_text "output.flv"

# 或者直接转为 webm
ffmpeg -i input.gif -preset veryslow -r 20 -crf 18 -b:v 1M output.webm


# mp4 转 gif（必须缩小分辨率，否则转出的图会变得非常大！）
# fps=20                    即设置帧率
# scale=-1:-1:flags=lanczos 表示分辨率维持不变
# -loop 0                   表示 gif 内容被循环播放的次数，0 表示无限循环播放
ffmpeg -i input.mp4 -vf "fps=20,scale=320:-1:flags=lanczos" -c:v pam -f image2pipe - | convert -delay 10 - -loop 0 -layers optimize output.gif
```

mkv/mp4/flv/webm 格式互转

```shell
# 直接复制所有内容
# -c copy        同时设定 video/audio 的编码器(encoder)为 copy
# -c:s mov_text  字幕也直接复制（mp4 的独立字幕，部分播放器可能不支持）
ffmpeg -i "input.mkv" -c copy -c:s mov_text "output.mp4"
ffmpeg -i "input.mkv" -c copy -c:s mov_text "output.flv"
ffmpeg -i "input.flv" -c copy -c:s mov_text "output.mkv"

# 批量转格式，直接复制内容
for $item in `find . -name "*.mkv"` do ffmpeg -i "$item" -c copy "$item.mp4"

# 重新使用 h264 进行编码
# -c:a copy      音频编码器，直接拷贝
# -c:v libx264   视频使用 x264 重新编码
# -c:s mov_text  字幕也直接复制（mp4 的独立字幕，部分播放器可能不支持）
# -b:v 6M        视频码率(bit rate)，1080p/24fps 推荐 5M-12M，10M 的话大概 14 分钟 1G 空间。
# -crf           是质量参数，建议值设在 18-28 之间（越小越接近无损，默认 23）建议自己多测测，看看效果
ffmpeg -i "xxx.mkv" -c:a copy -c:s mov_text -c:v libx264 -crf 23 "xxx.mp4"

# mp4 等格式转为 webm
## -c:v libvpx-vp9   由于 webm 使用专用的 vp9 编解码器，而不是 h264，这里需要使用 libvpx-vp9 重新编码
## -b:v 1M            视频码率(bit rate)，1080p/24fps 推荐 5M-12M，10M 的话大概 14 分钟 1G 空间。
# -c:a libopus       音频编码器
# -b:a 128k          音频码率(bit rate) 128k
# -crf               是质量参数，建议值设在 18-28 之间（越小越接近无损，默认 23）建议自己多测测，看看效果
ffmpeg -i input.mp4 -c:v libvpx-vp9 -b:v 1M -c:a libopus -b:a 128k -crf 23 output.webm
```

flv 等其他视频的互相转换，也是使用同样的命令。

编码的详细参数参见 [不同编码器特有的设定](https://gloomy-ghost.gitbooks.io/-ffmpeg/content/08-differente-encoders-special-options.html#%E5%AD%A6%E4%BC%9A%E7%9C%8B%E6%96%87%E6%A1%A3)


### 2. 视频压缩

如果有大量视频需要转码，可能更推荐使用「bilibili 压制工具或者「小丸工具箱原版」（仅支持 windows）。


### 3. 视频截取

待续


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
