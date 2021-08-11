在 QEMU 中使用 cloud-init 进行虚拟机初始化
---

参考 [../ProxmoxVE/README.md](../ProxmoxVE/README.md)，在本机的 KVM 环境中，也可以使用 cloud-init 来初始化虚拟机。
好处是创建虚拟机的时候，就能设置好虚拟机的 hostname/network/user-pass/disk-size 等一系列参数。

这需要用到一个工具：[cloud-utils](https://github.com/canonical/cloud-utils)

```shell
# manjaro
sudo pacman -S cloud-utils

# ubuntu
sudo apt install cloud-utils

# opensuse，包仓库里找不到 cloud-utils，只能源码安装
git clone https://github.com/canonical/cloud-utils
git checkout 0.32
cd cloud-utils && sudo make install
# 生成 iso 文件还需要 genisoimage，请使用一键安装：https://software.opensuse.org/package/genisoimage
```

`cloud-utils` 提供 cloud-init 相关的各种实用工具，
其中有一个 `cloud-localds` 命令，可以通过 cloud 配置生成一个非 cloud 的 bootable 磁盘映像，供本地的虚拟机使用。

首先编写 `user-data`:


```yaml
#cloud-config
hostname: opensuse15-2
fqdn: opensuse15-2.local  
# 让 cloud-init 自动更新 /etc/hosts 中 localhost 相关的内容
manage_etc_hosts: localhost

package_upgrade: true

disable_root: false

# 设置 root 的 ssh 密钥
user: root
# 设置密码，仅用于控制台登录
password: xxxxx
# 使用密钥登录
ssh_authorized_keys:
  - "<ssh-key content>"
chpasswd:
  # expire 使密码用完即失效，用户每次登录都需要设置并使用密码！
  expire: false
  
# ssh 允许密码登录（不建议开启）
ssh_pwauth: false
```

>注意 `user-data` 的第一行的 `#cloud-config` 绝对不能省略！它标识配置格式为 `text/cloud-config`！

再编写 `network-config`(其格式和 ubuntu 的 netplan 基本完全一致):

```yaml
version: 2
ethernets:
  eth0:
    dhcp4: false
    addresses: 
    - 192.168.122.160/24

    # TODO: 目前发现如下两个配置无法生效：默认网关，以及 dns servers
    gateway4: 192.168.122.1
    nameservers:
      addresses:
      - 192.168.122.1
      - 8.8.8.8
      search:
      - 'pve.local'
```

```shell
cloud-localds seed.iso user-data --network-config network-config
```

这样就生成出了一个 seed.iso，创建虚拟机时同时需要载入 seed.iso 和 cloud image，cloud-image 自身为启动盘，这样就大功告成了。
示例命令如下：

```shell
virt-install --virt-type kvm \
  --name k8s-master-0 \
  --vcpus 2 --memory 3072 \
  --disk k8s-master-0.qcow2,device=disk,bus=virtio \
  --disk ../vm-seeds/160-seed-k8s-master-0.iso,device=cdrom \
  --os-type linux \
  --os-variant opensuse15.3 \
  --network network=default,model=virtio \
  --graphics vnc \
  --import
```

也可以使用 virt-viewer 的 GUI 界面进行操作。

这样设置完成后，cloud 虚拟机应该就可以启动了，可以检查下 hostname、网络、root 的密码和私钥、ssh 配置是否均正常。

一切正常后，还有个问题需要解决——初始磁盘应该很小。可以直接手动扩容 img 的大小，cloud-init 在虚拟机启动时就会自动扩容分区：

```shell
qemu-img resize ubuntu-server-cloudimg-amd64.img 30G
```

## 画外：cloudinit 主机名称

cloudinit 有三个参数与 hostname 相关。其中有两个，就是上面提到的 `user-data` 中的：
1. hostname: 主机名称
2. fqdn: 主机的完全限定域名，优先级比 `hostname` 更高

这两个参数的行为均受 `preserve_hostname: true/false` 这个参数的影响。

另一个是 `meta-data` 中，可以设置一个 `local-hostname`，此参数的地位好像和 `user-data` 中的 `hostname` 相同，不过可能优先级会高一些吧。
没有找到相关文档。

## 相关文档

- [在 QEMU 使用 Ubuntu Cloud Images](https://vrabe.tw/blog/use-ubuntu-cloud-images-with-qemu/)

