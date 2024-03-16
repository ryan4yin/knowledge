# Nginx 学习笔记

## 1. Nginx 的四个主要组成部分

- Nginx 二进制可执行文件：由各模块源码编译出的单个可执行文件
- nginx.conf 配置文件: 控制 Nginx 的行为
- access.log 访问日志：记录每一条 http 请求的信息
- error.log 错误日志：定位问题

## 2. 编译一个定制的 Nginx

前面介绍了，Nginx 自身是单个可执行文件，因此要添加或移除任何模块，都需要修改编译参数、手动编译。

## 参考信息

- [Nginx核心知识100讲](https://time.geekbang.org/course/intro/100020301)
