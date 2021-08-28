Linux 服务器在使用过程中可能会遇到各种问题，其中之一就是“没有可用空间”。

遇到这种情况，就需要进行排查，定位到消耗了磁盘的那个文件夹。

流程如下：

## 1. `df -h`

`df -h` 会显示出所有挂载点的磁盘空间使用情况。`-h` 表示以 1k、1M、1G 为单位。

```
Filesystem(文件系统)      Size  Used Avail Use% Mounted on(分区)
/dev/mapper/centos-root   98G  6.1G   92G   7% /
devtmpfs                 4.8G     0  4.8G   0% /dev
tmpfs                    4.9G     0  4.9G   0% /dev/shm
tmpfs                    4.9G   33M  4.8G   1% /run
tmpfs                    4.9G     0  4.9G   0% /sys/fs/cgroup
/dev/sda1               1014M  189M  826M  19% /boot
tmpfs                    984M     0  984M   0% /run/user/0
overlay                   98G  6.1G   92G   7% /var/lib/docker/overlay2/8671cfef128ee6418ab1796ebba47b23283fdf1d338431b4a4ebdc2786485000/merged
shm                       64M     0   64M   0% /var/lib/docker/containers/d945d7043afb824a94ab8e11c3f61354945e40602b0212eb6cd1a794a5c2c475/mounts/shm
overlay                   98G  6.1G   92G   7% /var/lib/docker/overlay2/c24f633841568bb4672931f2da809b47335be7f085bf23237af2cd15bddc27a1/merged
shm                       64M     0   64M   0% /var/lib/docker/containers/e685309b470dde35837620928ba67d404722c4bba475f84ed0cb6ca823504907/mounts/shm
overlay                   98G  6.1G   92G   7% /var/lib/docker/overlay2/62cc31effdbb439942c43f1341b6b07fd933200b6c27a52c6a88ac4b63ae93e6/merged
shm                       64M     0   64M   0% /var/lib/docker/containers/7f7593fc8d14ddbe7dd1a946ccf08adf2bef415a7560db1c12d0ab0abb9e582a/mounts/shm
```

可以看到主分区 `/` 已经使用了 7%，现在假设因为某个软件的缓存，导致这个分区 `/` 的可用空间不多了。现在要排查到缓存所在位置。

## `du -h --max-depth=1`

df 是查看各挂载点的空间使用情况，而 du 是用于查看各目录/文件的大小。

我们需要找到 `/` 分区中真正消耗掉内存的那个文件/文件夹。

1. 首先 `cd /`
1. 使用 du 命令查看该目录下的空间使用情况：`du -h --max-depth=1`

```
[root@192-168-1-64 ~]# du -h --max-depth=1
157M    ./boot
0       ./dev
du: cannot access './proc/12646/task/12646/fd/4': No such file or directory
du: cannot access './proc/12646/task/12646/fdinfo/4': No such file or directory
du: cannot access './proc/12646/fd/4': No such file or directory
du: cannot access './proc/12646/fdinfo/4': No such file or directory
0       ./proc
33M     ./run
0       ./sys
34M     ./etc
26M     ./root
4.5G    ./var
0       ./tmp
1.6G    ./usr
0       ./home
0       ./media
0       ./mnt
2.6G    ./opt
0       ./srv
8.8G    .
```

在输出结果中找到占用磁盘过多的文件夹，cd 进去，再继续执行 `du -h --max-depth=1` 命令查看。

如此查看几次，一般就能定位到问题文件夹。

通过这样的排查，发现公司这次遇到的问题，是 elasticsearch 的数据文件夹把磁盘消耗光了。

定位到问题后，再依据该数据的重要程度，来决定是直接清空，还是如何处理它。


## 参考

- [linux 硬盘满了如何处理](https://blog.csdn.net/ck3207/article/details/76691904)