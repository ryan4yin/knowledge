常见问题与 Bugs
---

## 操作常见问题

1. 对于还没有安装 `qemu-guest-agent` 的任何主机，或者已经无响应的主机，千万不要点 `shutdown` 按钮，因为一定会失败！
2. 对于任何卡住的 `shutdown` 操作，一定要先手动在下方的面板中双击它然后点「stop」停止该操作，否则它会锁住该虚拟机，导致后续的所有操作都会卡住并失败！

## can’t lock file ‘/var/lock/qemu-server/lock-xxx.conf’ – got timeout

PVE 虚拟机卡在 BIOS 系统引导这一步，无法启动，也无法关机/强制关机/重置！

解决方法：手动删除掉 lockfile: `/var/lock/qemu-server/lock-xxx.conf`

因为虚拟机还卡在 BIOS 引导这一步，删除掉 lockfile 再关闭虚拟机并不会导致数据丢失。

## 集群有一个节点宕机，如何解除关联？

将多个节点组成一个 PVE Cluster 是很自然的一个选择，它能提供虚拟机热迁移（同 CPU 供应商）、统一管理面板等非常方便的功能。
但是这会带来集群级别的高可用问题。

根据官方文档 [Cluster_Manager - Proxmox](https://pve.proxmox.com/wiki/Cluster_Manager)，如果你需要容忍一定数量的节点宕机，PVE Cluster 至少需要三台主机（这跟 Etcd 一样，是 Raft 共识算法的要求），并且所有节点的 PVE 版本要完全一致。

那么如果节点除了问题，无法修复，该如何将它踢出集群呢？


如果节点仍然处于可用状态，宕机节点数低于 1/2，流程如下：

- 首先通过访问节点的 shell 界面，通过命令 `pvecm nodes` 确认集群的所有节点
- 将需要移除的节点彻底关机，并且确保它不会以当前配置再次启动（也就是说关机后需要清空硬盘，避免数据混乱）
- 通过命令 `pvecm delnode xxx` 将问题节点移除集群
- 将旧节点清理干净，重新装机。

如果你的集群只有 2 个节点，或者有超过 3 个节点但是有超过 1/2 不可用且无法恢复，那出于数据一致性要求，上面的流程就走不通了。会报错 `cluster not ready - no quorum?` 这时需要首先修改配置，使剩下的节点重新达成一致。其实就是修改选主节点时的投票数。

对于 2 个节点但挂掉 1 个的情况，首先执行如下指令允许当前节点自己选主：

```shell
# 设置只需要 1 票就能当前主节点
# 潜在问题是可能有些集群元数据只在损坏节点上有，这么改会导致这些数据丢失，从而造成一些问题。
# 安全起见，建议在修复集群后，再重启一遍节点...
pvecm expected 1
```

现在 quorum 就已经恢复了，可以走前面给出的节点移除流程。

如果 corosync 完全无法启动，上面给出的命令也会修改选主投票参数也会失败，这时可以直接手动修改 `/etc/corosync/corosync.conf` 使 corosync 能正常启动。


## ubuntu cloud image 的坑

- ubuntu 启动时会报错 `no such device: root`，但是过一会就会正常启动。
  - 这是 ubuntu cloud image 的 bug: https://bugs.launchpad.net/cloud-images/+bug/1726476
- ubuntu 启动后很快就会进入登录界面，但是 root 密码可能还没改好，登录会报密码错误，等待一会再尝试登录就 OK 了
- ubuntu 的默认网卡名称是 ens3，不是 eth0，注意修改 network_config 的网卡名称，否则网络配置不会生效

## opensuse cloud image 的坑

- opensuse leap 15 只支持 network_config v1，对 v2 的支持有 bug，`gateway4` 不会生效


## debian cloud image 的坑

debian 的 cloud 镜像根本没法用，建议避免使用它。

- debian 启动时会彻底卡住，或者直接报错 kernel panic
  - 原因是添加了 spice 图形卡，换成 vnc 就正常了
- [Debian Cloud Images](https://cdimage.debian.org/cdimage/cloud/) 中的 nocloud 镜像不会在启动时运行 cloudinit，cloudinit 完全不生效
  - 不知道是啥坑，没解决

## 克隆创建的虚拟机，卡在 `Booting from Hard Disk...` 状态

被用做模板的虚拟机可以正常启动，但是克隆的虚拟机就卡住了。

可能的原因：

1. 磁盘有问题，出这个问题的 cloud image 是 `ubuntu-20.10-server-cloudimg-amd64.img`，我更换成 `ubuntu-20.10-server-cloudimg-amd64-disk-kvm.img` 就没问题了。
   1. 磁盘镜像均下载自 https://cloud-images.ubuntu.com/releases/groovy/release-20201210/
2. BIOS 不匹配：将 BIOS 从 SeaBIOS 切换到 UEFI


## 虚拟机启动时 cloudinit 报错 faild to start OpenBSD Secure Shell server 

有如下几种可能：

### 可能性一：虚拟机名称包含非法字符

pve 的 cloudinit 配置会在启动时尝试将虚拟机 hostname 修改为与虚拟机一致，但是又没有对虚拟机名称做合法性校验...

当你使用的虚拟机名称包含了非法字符时就会出这个问题，比如 `ubuntu-22.10-cloudimage-template`，其中的 `.` 就是非法的， `.` 在 DNS 中用于划分不同的域！

解决方法：克隆个新虚拟机，将名称改为合法名称，问题就解决了。

### 可能性二：磁盘空间不足

qcow 镜像转换成的虚拟机磁盘很小，只有 2G，如果不扩容，启动时就会出各种奇怪的问题。

解决方法：通过 Web UI 扩容磁盘大小，建议至少给 32G。

## 无法修改虚拟机的 Hostname

如前所述，pve 的 cloudinit 配置会在启动时尝试将虚拟机 hostname 修改为与虚拟机一致，这导致手动修改无法生效无效。

解决方法见如下分析：

### cloud-init 高级配置

PVE 使用 CDROM 只读盘(/dev/sr0)来进行 cloud-init 的配置。
在虚拟机启动后，/dev/sr0 将被卸载。

可挂载上该只读盘，查看其中的初始化配置内容：

```shell
$ mkdir cloud-config
$ mount /dev/sr0 cloud-config
mount: /dev/sr0 is write-protected, mounting read-only
$ ls cloud-config
meta-data  network-config  user-data
```

查看上述文件发现 `user-data` 有如下问题：

1. 它硬编码了 `manage_etc_hosts: true`，这导致我手动在 `/etc/cloud/cloud.cfg` 里设定的 `manage_etc_hosts: false` 被覆盖。
2. 它设置了 `hostname: <vm-name>`
   1. cloud-init 的默认策略是 `preserve_hostname: false`，表示不维持对 `hostname` 的修改。
   2. 默认策略的实际行为：每次虚拟机启动时，cloud-init 都会自动将 `/etc/hostname` 还原为 `user-data` 中的 `hostname`/`fqdn`.
   3. 这使任何对 `/etc/hostname` 的手动修改，都是临时的，重启就会被还原为 `user-data` 中设置的 `hostname`.

### 修改 cloud-init 相关的硬编码参数

通过前面的排查，我们发现 proxmox 有很多参数都硬编码了，没有通过配置暴露出来，导致我们无法修改。

为了解决这个问题，我们完全可以修改掉 PVE 代码里的硬编码参数。

首先通过全文搜索，找到硬编码参数的位置：

```shell
# 在 /usr/share 中全文搜索 manage_etc_hosts 这个关键字
grep -r manage_etc_hosts /usr/share
```

直接就搜索到了硬编码位置是 `/usr/share/perl5/PVE/QemuServer/Cloudinit.pm`

1. 手动将配置修改为 `manage_etc_hosts: localhost`，就能让 cloud-init 只更新 localhost 相关的 hosts 内容。

2. 如果希望对 hostname 的手动修改能永久生效，可以添加参数 `preserve_hostname: true`.
   1. 注意这样设置后，cloud-init 的 `set_hostname`/`update_hostname` 两个模块将不会修改 hostname！

对上述文件的修改需要重启 PVE 后，才能生效(因为 perl 程序才启动后代码就加载到内存中了，改文件对内存中的对象没有影响)。
