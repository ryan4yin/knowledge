# 动手实现一个容器工具


## 一、Linux Namespace

Linux 提供了六种名字空间用于在内核中隔离出多个运行环境：

 | 分类  | 系统调用参数  | 功能 | 相关内核版本 | 
 | :---: |    :---:    |   :---:   |  :---:   |
 | Mount namespaces  | CLONE_NEWNS | 隔离 hostname/doaminname  | Linux 2.4.19 | 
 | UTS namespaces  | CLONE_NEWUTS  |     | Linux 2.6.19 | 
 | IPC namespaces  | CLONE_NEWIPC  |     | Linux 2.6.19 | 
 | PID namespaces  | CLONE_NEWPID  |     |Linux 2.6.24 | 
 | Network namespaces  | CLONE_NEWNET |  | 始于Linux 2.6.24 完成于 Linux 2.6.29 | 
 | User namespaces  | CLONE_NEWUSER  |   |  始于 Linux 2.6.23 完成于 Linux 3.8 | 


## 参考

- [动手实现 mydocker](https://github.com/xianlubird/mydocker)

- [Linux Namespace 技术与 Docker 原理浅析](https://creaink.github.io/post/Computer/Linux/Linux-namespace.html)
- [Linux Namespace 入门系列：Namespace API - 米开朗基杨](https://www.cnblogs.com/ryanyangcs/p/12591372.html)
- [docker 容器基础技术：linux cgroup 简介](https://cizixs.com/2017/08/25/linux-cgroup/)


参考的运行时：

- [containers/youki](https://github.com/containers/youki)

