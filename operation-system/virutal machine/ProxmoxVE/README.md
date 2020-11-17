# [Proxmox Virtual Environment](https://pve.proxmox.com/)

PVE 是一个开源免费，订阅收费的服务器虚拟化系统，基于 QEMU/KVM.

和 ESXi 相比，它的优势有：

1. PVE 开源免费，而 VMware 的全套技术都是闭源收费的
1. PVE 底层是 QEMU/KVM，存储方案也是 Ceph/iSCSI/NFS/LVM 这些都是使用很广泛的开源技术，学会了还可以应用在别的地方。
2. 提供一套方便的 CLI 工具，以及 RESTful API。不论是 CLI、HTTP API 还是 [Python SDK](https://github.com/proxmoxer/proxmoxer)，又或者 terraform 支持，PVE 都比 ESXi 要好用很多！
3. 文档齐全，而且很接地气，还包含许多 QEMU/KVM/CEPH 等开源技术的内容。 反观 VMware 的文档，真的是写得烂得一批。

缺点在于，PVE 的 WebUI 功能不全，有些功能必须通过命令行才能实现。（这和路由器类似，高级功能只有 CLI 支持）

## 安装　PVE

安装过程没啥好说的，安装好后，需要按下面这篇文章配置国内镜像源，启用 root 账户　ssh 登录：

- [虚拟服务器软件 PVE 踩坑记](https://fengtalk.com/216.html)


## 使用 Cloud-Init 自动配置网卡、SSH密钥、存储大小配置

>完全参照官方文档 [Cloud-Init_Support - PVE Docs](https://pve.proxmox.com/wiki/Cloud-Init_Support)

首先下载 Cloud 版本的系统镜像：

1. [CentOS Cloud 版本](https://cloud.centos.org/centos/): 提供 qcow2 格式的镜像
2. [Debian Cloud Images](https://cdimage.debian.org/cdimage/cloud/): 也提供 qcow2 格式的镜像
3. [Ubuntu Cloud Images (RELEASED)](https://cloud-images.ubuntu.com/releases/): 提供 img 格式的裸镜像（PVE 也支持此格式）

上述镜像和我们普通虚拟机使用的 ISO 镜像的区别，一是镜像格式不同，二是都自带了 cloud-init 和 [Qemu-guest-agent](https://pve.proxmox.com/wiki/Qemu-guest-agent)。

上述三个 cloud 镜像的默认名称和系统名称完全一致，分别为 `centos`/`debian`/`ubuntu`，
均没有默认密码，并且禁用了 SSH 密码登录，必须通过 cloud-init 设置私钥方式进行远程登录。

建议在 cloud-init 配置中自行设置账号与私钥，不要使用默认的账号名。
比如测试环境，可以直接设置账号为 root，并设置相应的私钥。

接下来我们需要将得到的 qcow2 镜像导入 PVE，并用它创建一个虚拟机模板。

首先创建虚拟机，并以导入的磁盘为该虚拟机的硬盘

```shell
# 创建新虚拟机
qm create 9000 --memory 2048 --net0 virtio,bridge=vmbr0

# 将下载好的 img/qcow2 镜像导入为新虚拟机的硬盘
qm importdisk 9000 bionic-server-cloudimg-amd64.img local-lvm

# 通过 scsi 方式，将导入的硬盘挂载到虚拟机上
qm set 9000 --scsihw virtio-scsi-pci --scsi0 local-lvm:vm-9000-disk-1
```


```shell
# 创建一个 cloud-init 需要使用的 CDROM 盘
qm set 9000 --ide2 local-lvm:cloudinit
# 设置系统引导盘
qm set 9000 --boot c --bootdisk scsi0
# 设置 serial0 为显示终端，很多云镜像都需要这个。（？感觉我不需要？）
qm set 9000 --serial0 socket --vga serial0
```

后续配置：
1. 手动设置 cloud-init 配置，启动虚拟机。
1. 进入虚拟机后，安装所需的基础环境，如 docker/docker-compose/vim/git/python3
2. 关闭虚拟机，然后将虚拟机设为模板（只读）。
3. 接下来就可以从这个模板虚拟机，克隆各类新虚拟机了~

## 解决 SSH 登录速度慢的问题

貌似所有的 cloud-init 的虚拟机，SSH 都存在速度慢的问题。
关闭掉 ssh server 的反向 DNS 解析，可以解决这个问题：

```shell
echo "UseDNS no" >> /etc/ssh/sshd_config
```

##　自动化工具

- [terraform-provider-proxmox](https://github.com/Telmate/terraform-provider-proxmox): 详情参见 [terraform - infrastructure](/infrastructure/terraform/README.md)
- [Python SDK](https://github.com/proxmoxer/proxmoxer)

## 监控告警

- [prometheus pve expoter](https://github.com/prometheus-pve/prometheus-pve-exporter): 通过 prometheus+grafana 监控 PVE 集群



## 常见问题

### 1. 导入已有的 qcow2 镜像

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


## 相关文档

- [Proxmox Wiki](https://pve.proxmox.com/wiki/Main_Page)
- [配置Cloud-Init工具 - 华为云](https://support.huaweicloud.com/usermanual-ims/ims_01_0407.html)