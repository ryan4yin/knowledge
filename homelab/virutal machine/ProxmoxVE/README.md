# [Proxmox Virtual Environment](https://pve.proxmox.com/)

PVE 是一个开源免费，订阅收费的服务器虚拟化系统，基于 QEMU/KVM.

## 安装　PVE

安装过程没啥好说的，安装好后，需要按下面这篇文章配置国内镜像源，启用 root 账户　ssh 登录：

```shell
# 设置 debian 的阿里镜像源
cp /etc/apt/sources.list /etc/apt/sources.list.bak
sed -i "s@\(deb\|security\).debian.org@mirrors.aliyun.com@g" /etc/apt/sources.list

# 去除烦人的订阅提示
sed -i "s/data.status !== 'Active'/false/g" /usr/share/javascript/proxmox-widget-toolkit/proxmoxlib.js

# 设置 pve 国内镜像源
# https://mirrors.bfsu.edu.cn/help/proxmox/
echo 'deb https://mirrors.bfsu.edu.cn/proxmox/debian buster pve-no-subscription' > /etc/apt/sources.list.d/pve-no-subscription.list
```


## 使用 Cloud-Init 自动配置网卡、SSH密钥、存储大小配置

>完全参照官方文档 [Cloud-Init_Support - PVE Docs](https://pve.proxmox.com/wiki/Cloud-Init_Support)

首先下载 Cloud 版本的系统镜像（注意：下面的几种镜像都分别有自己的坑点...有时候可能不是你配置问题，单纯地是镜像的 bug...）：

1. [Ubuntu Cloud Images (RELEASED)](https://cloud-images.ubuntu.com/releases/): 提供 img 格式的裸镜像（PVE 也支持此格式）
   - 请下载带有 .img 结尾的镜像，其中 `kvm.img` 结尾的镜像会更精简一点。
2. [OpenSUSE Cloud Images](https://download.opensuse.org/repositories/Cloud:/Images:/)
   - 请下载带有 NoCloud 或者 OpenStack 字样的镜像。
3. 对于其他镜像，可以考虑手动通过 iso 来制作一个 cloudinit 镜像，参考 [openstack - create ubuntu cloud images from iso](https://docs.openstack.org/image-guide/ubuntu-image.html)

>注：[Debian Cloud Images](https://cdimage.debian.org/cdimage/cloud/) 的镜像无法使用，其他 ubuntu/opensuse 的 cloud 镜像也各有问题... 详见 [Bugs 统计页](./Bugs.md)

上述镜像和我们普通虚拟机使用的 ISO 镜像的区别，一是镜像格式不同，二是都自带了 `cloud-init`/`qemu-guest-agent`/`cloud-utils-growpart` 等 cloud 相关软件。

其中 NoCloud 表示支持 cloudinit NoCloud 数据源——即使用 `seed.iso` 提供 user-data/meta-data/network-config 配置，PVE 就是使用的这种模式。
而 Openstack 镜像通常也都支持 NoCloud 模式，所以一般也是可以使用的。

cloud image 基本都没有默认密码，并且禁用了 SSH 密码登录，必须通过 cloud-init 设置私钥方式进行 ssh 登录。

建议在 cloud-init 配置中自行设置账号与私钥，不要使用默认的账号名。
比如测试环境，可以直接设置账号为 root，并设置相应的私钥。

接下来我们需要将得到的 qcow2 镜像导入 PVE，并用它创建一个虚拟机模板。

首先创建虚拟机，并以导入的磁盘为该虚拟机的硬盘

```shell
# 创建新虚拟机
qm create 9000 --name ubuntu-bionic-template --memory 2048 --net0 virtio,bridge=vmbr0

# 将下载好的 img/qcow2 镜像导入为新虚拟机的硬盘
qm importdisk 9000 ubuntu-20.10-server-cloudimg-amd64.img local-lvm

# 通过 scsi 方式，将导入的硬盘挂载到虚拟机上
qm set 9000 --scsihw virtio-scsi-pci --scsi0 local-lvm:vm-9000-disk-0

# qcow2 镜像默认仅 2G 大小，需要手动扩容到 32G，否则虚拟机启动会报错
qm resize 9000 scsi0 32G
```


```shell
# 创建一个 cloud-init 需要使用的 CDROM 盘(sr0)
qm set 9000 --ide2 local-lvm:cloudinit
# 设置系统引导盘
qm set 9000 --boot c --bootdisk scsi0
# 设置 serial0 为显示终端，很多云镜像都需要这个。（？感觉我不需要？）
qm set 9000 --serial0 socket --vga serial0
```

后续配置：
1. 手动设置 cloud-init 配置，启动虚拟机，并通过 ssh 登入远程终端。
2. 检查 qemu-guest-agent，如果未自带，就需要手动安装它
   1. ubuntu 需要通过 `sudo apt install qemu-guest-agent` 手动安装它
3. 安装所需的基础环境，如 docker/docker-compose/vim/git/python3
4. 关闭虚拟机，然后将虚拟机设为模板（只读）。
5. 接下来就可以从这个模板虚拟机，克隆各类新虚拟机了~

## 一些遇到的坑

## 解决 SSH 登录速度慢的问题

貌似所有的 cloud-init 的虚拟机，SSH 都存在速度慢的问题。
关闭掉 ssh server 的反向 DNS 解析，可以解决这个问题：

```shell
echo "UseDNS no" >> /etc/ssh/sshd_config
```

## 虚拟机硬盘扩容

CentOS/Ubuntu/Debian 提供的 Cloud 镜像，都自带了 cloud-utils-growpart 这个组件，可以实现在扩容物理硬盘时，自动调整 Linux 的分区大小。

因此需要扩容虚拟机时，直接通过 UI 面板/命令行扩容虚拟机的硬盘即可， Linux 的分区会被 cloud-utils-growpart 自动扩容。

>因为这个方便的特性，也为了减少虚拟化的开销，Cloud 镜像默认是不使用 LVM 逻辑分区的。
LVM 逻辑分区虽然方便，但是它对物理机的作用更大些。虚拟机因为本身就能动态扩容“物理硬盘”的大小，基本不用不到 LVM。

>还有一点，就是虚拟机通常只需要一个根分区就行，尤其是归 openstack/kubernetes 管的虚拟机。
只有在使用分布式存储之类的场景下，数据需要独立存储，才需要用到额外的分区(/data 之类的)。
一般只有物理机，才需要像网上很多文章提的那样，为 /boot / /home 去单独分区。
而且现在大家都用 SSD 了，物理机这样做分区的都少了，比如我个人电脑，就是一个 / 分区打天下。。。

##　自动化工具

- terraform-provider-proxmox: 详情参见 [terraform - infrastructure](/infrastructure/terraform/README.md)
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
- [canonical/cloud-init - github](https://github.com/canonical/cloud-init)
- [Run Amazon Linux 2 as a virtual machine on premises](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/amazon-linux-2-virtual-machine.html)
