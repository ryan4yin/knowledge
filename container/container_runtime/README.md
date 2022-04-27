# 动手实现一个容器工具


## 一、Linux Namespace

Linux 提供了许多名字空间用于在内核中隔离出多个运行环境，可以通过 `man namespaces` 查看其文档。

名字空间的隔离其实就是一种障眼法，它实际上是修改了名字空间中的进程看待整个计算机的「视图」，即这些进程的「视线」被操作系统做了限制，只能「看到」某些指定的内容。但对于宿主机来说，这些被「隔离」了的进程跟其他进程并没有太大区别。

目前 Linux 有这几个名字空间：

 | 分类  | 系统调用参数  | 功能 | 相关内核版本 | 
 | :---: |    :---:    |   :---:   |  :---:   |
 | Mount namespaces  | CLONE_NEWNS |  实现文件系统挂载点的隔离   | Linux 2.4.19 | 
 | UTS namespaces  | CLONE_NEWUTS  |  隔离 hostname/doaminname，这俩分别通过 `sethostname()`/`setdomainname()` 设置  | Linux 2.6.19 | 
 | IPC namespaces  | CLONE_NEWIPC  |  隔离信号量、消息队列和共享内存  | Linux 2.6.19 | 
 | PID namespaces  | CLONE_NEWPID  |  隔离进程编号   | Linux 2.6.24 | 
 | Network namespaces  | CLONE_NEWNET | 隔离网络设备、网络栈、端口等等 | 完成于 Linux 2.6.29 | 
 | User namespaces  | CLONE_NEWUSER  |  隔离用户和用户组 |  完成于 Linux 3.8 | 
 | Time namespaces  | CLONE_NEWTIME  |  隔离系统的 `CLOCK_MONOTONIC`（抛去休眠的系统启动时间） 与 `CLOCK_BOOTTIME`（系统启动时间，包含休眠时间）,但是不包含 `CLOCK_REALTIME` |  Linux 5.6 | 


名字空间涉及到三个系统调用:

1. `int clone(int (*child_func)(void *), void *child_stack, int flags, void *arg)`: 和 `fork` 一样是创建新进程的系统调用，但是它可以通过 `flags` 来创建 Namespaces，并将新进程放到这些 namespaces 中运行。
2. `int unshare(int flags)`: 与 `clone` 不同的是，`unshare` 直接操作当前进程，将它从当前 Namespaces 分离，加入到新创建的进程中。此系统调用只有一个参数：`flags`.
3. `int setns(int fd, int nstype)`: 将指定的进程从当前 namespaces 上分离，然后加入到已经存在的其他 namespaces 中。

另外 Linux 系统还提供了一个 `unshare` 命令，但是它的功能更类似 `clone` 系统调用——创建新的名字空间，然后在新名字空间中运行某个程序：

```shell
# 在一个所有名字空间均与当前环境隔离的环境中，运行程序
# 第一行全都是设置名字空间的参数
# --map-root-user 将当前用户映射为新 user namespace 中的 root 用户（superuser）
# --mount-proc 在 mount namespaces 中挂在了一个新的虚拟 /proc 文件夹
# --fork --kill-child 表示以子进程的方式启动新程序，并且在 unshare 退出时把这个子进程也干掉。
$ unshare --ipc --mount --net --pid --uts --user \
    --map-root-user \
    --mount-proc --fork --kill-child /bin/bash

# 网络名字空间也是隔离的，新的 namespace 默认只会创建一个 lo 接口，而且是 DOWN 状态。
$ ip addr show
1: lo: <LOOPBACK> mtu 65536 qdisc noop state DOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00

# 独立的进程名字空间，/bin/bash 是 1 号进程
$ ps aux
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
nobody       1  0.0  0.0  11068  7884 pts/3    S    11:58   0:00 /bin/bash
nobody     753  0.0  0.0  10164  3480 pts/3    R+   12:01   0:00 ps aux
```

另一个和 namepsace 相关的命令是 `nsneter`，它对应系统调用 `setns`,用于在已经存在的名字空间运行程序，最常用于诊断容器状况等场景。

我们别关闭 `unshare` 窗口，再新开一个终端，尝试使用 nsenter 来进入到 `unshare` 创建的名字空间中：

```shell
# 首先查出 unshare 的进程 ID
$ ps aux | grep unshare
ryan      8101  0.0  0.0   5336   696 pts/3    S    12:31   0:00 unshare --ipc --mount --net --pid --uts --user --map-root-user --mount-proc --fork --kill-child /bin/bash
 
 # 通过进程 pid 查到其名字空间及子进程相关信息
$ pstree 8101 -Sp
unshare(8101,ipc,mnt,net,user,uts)───bash(8102,pid)

# 使用 nsenter 进入其所有名字空间执行命令（需要 root 权限）
# 也可通过 --net/--user/--pid 等来指定进入哪些名字空间
# 简单起见，也可以直接通过 nsenter 运行 /bin/sh 命令
$ nsenter --target 8101 --all ip addr show
1: lo: <LOOPBACK> mtu 65536 qdisc noop state DOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00

```

## 二、Linux Cgroups

前面提到的 Namespace 只是一个「障眼法」，它虽然欺骗了进程让它们以为自己是独占了系统，但是系统的所有资源，实际上是系统上所有的进程共享的，任何进程都能随时抢占掉整个系统的所有资源。

为了实现真正的隔离，我们还需要资源的限制技术，它就是 Linux Cgroups.

Linux Cgroups 全称是 Linux Control Group。它最主要的作用，就是限制一个进程组能够使用的资源上限，包括 CPU、内存、磁盘、网络带宽等等。

在 Linux 中，Cgroups 给用户暴露出来的操作接口是文件系统，理解使用上还是比较容易的。
它以文件和目录的方式组织在操作系统的 `/sys/fs/cgroup` 路径。可以使用 mount 把它展示出来：

```shell
# 注意，以下命令均需 root 权限
$ mount -t cgroup
cgroup on /sys/fs/cgroup/systemd type cgroup (rw,nosuid,nodev,noexec,relatime,xattr,release_agent=/usr/lib/systemd/systemd-cgroups-agent,name=systemd)
cgroup on /sys/fs/cgroup/cpuset type cgroup (rw,nosuid,nodev,noexec,relatime,cpuset)
cgroup on /sys/fs/cgroup/hugetlb type cgroup (rw,nosuid,nodev,noexec,relatime,hugetlb)
cgroup on /sys/fs/cgroup/pids type cgroup (rw,nosuid,nodev,noexec,relatime,pids)
cgroup on /sys/fs/cgroup/memory type cgroup (rw,nosuid,nodev,noexec,relatime,memory)
cgroup on /sys/fs/cgroup/net_cls,net_prio type cgroup (rw,nosuid,nodev,noexec,relatime,net_cls,net_prio)
cgroup on /sys/fs/cgroup/cpu,cpuacct type cgroup (rw,nosuid,nodev,noexec,relatime,cpu,cpuacct)
cgroup on /sys/fs/cgroup/freezer type cgroup (rw,nosuid,nodev,noexec,relatime,freezer)
cgroup on /sys/fs/cgroup/devices type cgroup (rw,nosuid,nodev,noexec,relatime,devices)
cgroup on /sys/fs/cgroup/blkio type cgroup (rw,nosuid,nodev,noexec,relatime,blkio)
cgroup on /sys/fs/cgroup/perf_event type cgroup (rw,nosuid,nodev,noexec,relatime,perf_event)
```

mount 列出的每一行是一个目录，它都对应一种 cgroups 可以限制的资源种类，而目录中的所有文件，则对应着这种资源可以被限制的方法。以 CPU 为例：

```shell
$ ls /sys/fs/cgroup/cpu
cgroup.clone_children  cpuacct.stat       cpuacct.usage_percpu       cpuacct.usage_sys   cpu.cfs_quota_us   cpu.shares  notify_on_release  tasks
cgroup.procs           cpuacct.usage      cpuacct.usage_percpu_sys   cpuacct.usage_user  cpu.rt_period_us   cpu.stat    release_agent      user.slice
cgroup.sane_behavior   cpuacct.usage_all  cpuacct.usage_percpu_user  cpu.cfs_period_us   cpu.rt_runtime_us  docker      system.slice
```

能看到它列出了许多的限制方法，还有个别文件夹。
其中的 `cpu.cfs_quota_us` 与 `cpu.cfs_period_us` 需要组合使用，表示限制在 `cpu.cfs_period_us` 这么长的时间段内，进程只能使用 `cpu.cfs_quota_us` 这么长的 CPU 时间。

`/sys/fs/cgroup/cpu` 中的每个文件夹，都是一个 cgroups 控制组的抽象，直接 `mkdir` 就是在创建不同的控制组。

```shell
$ cd /sys/fs/cgroup/cpu
$ mkdir test
# OS 会在控制组文件夹中自动生成该控制组对应的资源限制文件
$ ls test
cgroup.clone_children  cpuacct.stat   cpuacct.usage_all     cpuacct.usage_percpu_sys   cpuacct.usage_sys   cpu.cfs_period_us  cpu.rt_period_us   cpu.shares  notify_on_release
cgroup.procs           cpuacct.usage  cpuacct.usage_percpu  cpuacct.usage_percpu_user  cpuacct.usage_user  cpu.cfs_quota_us   cpu.rt_runtime_us  cpu.stat    tasks
```

接下来测试验证下 CPU 控制组的功能：

```shell
# 后台跑个小程序
$ while : ; do : ; done &
[1] 2320
# 能看到系统被使用了接近 100% 的 CPU
$ top
...
  PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND
 2320 root      20   0  125000   1248      0 R 100.0  0.0   5:46.03 bash
...
# 目前默认的配置是，在 100000us (100ms)内，不限制进程的 CPU 用量
$ cat /sys/fs/cgroup/cpu/test/cpu.cfs_quota_us 
-1
$ cat /sys/fs/cgroup/cpu/test/cpu.cfs_period_us 
100000

# 修改为只允许进程使用 20000us (20ms)
$ echo 20000 > /sys/fs/cgroup/cpu/test/cpu.cfs_quota_us

# 将我们后台进程的 id 写入到 test 控制组的 tasks 文件中，实现控制此进程的资源用量
$ echo 2320 > /sys/fs/cgroup/cpu/test/tasks

# 再 top 看看，就会发现 cpu 用量已经降到差不多 20% 了
$ top
...
  PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND
 2320 root      20   0  125000   1248      0 R  19.9  0.0   5:35.87 bash
...

# 可以继续手动调整 CPU 的限制值，再 top 观测

# 测试完成后关闭测试进程
$ kill 2320
```





## 参考

- [动手实现 mydocker](https://github.com/xianlubird/mydocker)

- [Linux Namespace 技术与 Docker 原理浅析](https://creaink.github.io/post/Computer/Linux/Linux-namespace.html)
- [Linux Namespace 入门系列：Namespace API - 米开朗基杨](https://www.cnblogs.com/ryanyangcs/p/12591372.html)
- [深入理解 Linux Cgroup 系列（一）：基本概念 -  - 米开朗基杨](https://www.cnblogs.com/ryanyangcs/p/11198140.html)
- [Linux Capabilities 入门教程：概念篇 - 米开朗基杨](https://www.cnblogs.com/ryanyangcs/p/11757559.html)
- [docker 容器基础技术：linux cgroup 简介 - cizixs](https://cizixs.com/2017/08/25/linux-cgroup/)


参考的运行时：

- [containers/youki](https://github.com/containers/youki)

