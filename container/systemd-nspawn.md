## [systemd-nspawn](https://wiki.archlinuxcn.org/wiki/systemd-nspawn)

> https://wiki.archlinuxcn.org/wiki/systemd-nspawn

systemd-nspawn 跟 chroot 命令类似，是个终极版的 chroot。

systemd-nspawn 将容器中各种内核接口的访问限制为只读，像是 /sys, /proc/sys 和 /sys/fs/selinux。网络接
口和系统时钟不能从容器内更改，不能创建设备节点。不能从容器中重启宿主机，也不能加载内核模块。

相比 lxc 或 libvirt， systemd-nspawn 更容易配置。

systemd-nspawn 是 systemd 的一部分并被打进 systemd 软件包中。

TODO
