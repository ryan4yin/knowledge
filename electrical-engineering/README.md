# 电子工程 Electrical Engineering

小时候同村的一个伙伴买了台遥控赛车，我们羡慕地不行，眼巴巴地希望他能多分一点时间给我玩。但是我从小到大从来没买过任何一台遥控赛车。

受限于金钱，大学学的也不是计算机，大学期间也从未接触过硬件，现在希望能在业余完成这个小时候的赛车玩具梦吧。
比如制作一台遥控小车、带有深度学习功能的自走小车、机器人手臂等等，都感觉很有意思。

更进一步，我能否做一些更有意思的东西呢？比如说机器人！


## 串口打开 TTY 界面

最简单的是直接使用 Linux 自带的 screen 界面：

```shell
# 让 screen 使用 256 全彩终端
export TERM=xterm-256color

# 登录到 /dev/ttyUSB0 这个串口的 TTY 页面，波特率设为 115200
screen /dev/ttyUSB0 15200

# 临时离开当前会话：先按 ctrl+a，然后再按 d 键
# 杀死当前会话并退出：c-a k
# 更多快捷键请 man screen 查看文档

# 显示后台运行的终端会话
screen -ls

# 重新进入某个终端会话（xxx 为会话 id）
screen -r xxx
```

## 我的学习计划

参见我的博客文章 [EE 入门 - 电子电路基础知识](https://thiscute.world/posts/electrical-engineering-circuits-basics-1/) 文末


## 相关难点对应的参考资料

 - [傅立叶变换交互式入门](https://www.jezzamon.com/fourier/zh-cn.html)

## 嵌入式相关的交流群与论坛

内容迁移至：[嵌入式相关的交流群与论坛 - Ryan4yin - 知乎](https://www.zhihu.com/question/352385472/answer/2921790194)

## 学习笔记

都分文件夹存在这个 README 的文件夹里了。

- [Makefile 学习笔记](https://github.com/ryan4yin/video2ascii-c/blob/master/Makefile)
- [CMake 学习笔记](./CMake-Usage.md)

### 进阶 - 机器人相关资料

- [how-to-learn-robotics](https://github.com/qqfly/how-to-learn-robotics)
- [gobot](https://github.com/hybridgroup/gobot)




