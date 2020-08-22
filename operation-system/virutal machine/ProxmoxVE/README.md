# [Proxmox Virtual Environment](https://pve.proxmox.com/)

PVE 是一个开源免费，订阅收费的服务器虚拟化系统，基于 QEMU/KVM.

和 ESXi 相比，它的优势有：

1. PVE 底层是 QEMU/KVM，存储方案也是 Ceph/iSCSI/NFS/LVM 这些都是使用很广泛的技术，学会了还可以应用在别的地方。
2. 提供一套方便的 CLI 工具，以及 RESTful API。不论是 CLI、HTTP API 还是 [Python SDK](https://github.com/proxmoxer/proxmoxer)，PVE 都比 ESXi 要好用很多！
3. 文档齐全，而且很接地气，还包含许多 QEMU/KVM/CEPH 等开源技术的内容。 反观 VMware 的文档，真的是写得烂得一批。

缺点在于，PVE 的 WebUI 功能不全，有些功能必须通过命令行才能实现。（这和路由器类似，高级功能只有 CLI 支持）


## 安装　PVE

安装过程没啥好说的，安装好后，需要按下面这篇文章配置国内镜像源，启用 root 账户　ssh 登录：

- [虚拟服务器软件 PVE 踩坑记](https://fengtalk.com/216.html)

## 常见问题

### 导入已有的 qcow2 镜像

>必须要命令行操作

先通过 scp 将 qcow2 传输到 PVE 上，然后命令行使用如下命令导入镜像：

```shell
# 命令格式
qm importdisk <vmid> <source> <storage>
# 示例
qm importdisk 201 vm-201-disk-1.qcow2 local-lvm
```

导入完成后，在 WebUI 界面的左侧会看到多了一个「未使用的磁盘 0」，
现在新建一台新虚拟机，然后删除掉默认的磁盘（分离+删除，要两步），然后挂载这个「未使用的磁盘 0」就大功告成了。


##　参考


