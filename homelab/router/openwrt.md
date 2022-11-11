# OpenWRT 路由专用系统


## 在 PVE 配置 OpenWRT 虚拟机

1. 下载最新的 OpenWRT 镜像
   1. 2022/11/11 最新版为 [22.03.2/targets/x86/64/](https://downloads.openwrt.org/releases/22.03.2/targets/x86/64/)，请下载其中第一个镜像文件 `generic-ext4-combined-efi.img.gz`
   2. 官方文档 [OpenWrt on x86 hardware (PC / VM / server)](https://openwrt.org/docs/guide-user/installation/openwrt_x86)
1. 在 PVE 中手动创建虚拟机，BIOS 使用 OVMF(UEFI) ，然后把默认磁盘卸载并删除
   1. OVMF 模式下会自动生成一个 uefi 硬盘，不需要去动它
   2. 为了确保性能，cpu 请选用 host 模式，配置建议给到 1C/0.5G - 2c/1G
2. 使用命令将下载的 `img` 文件导入到新建的虚拟机并挂载，然后将该磁盘增大 1G
   1. 导入命令（需要将 106 修改为虚拟机 ID）：`qm importdisk 106 openwrt-22.03.2-x86-64-generic-ext4-combined-efi.img local-lvm`
3. 修改启动顺序为仅从新硬盘启动：scsi0
4. 启动主机
5. 一开始会启动失败进入 UEFI shell，因为 openwrt 不支持「secure boot」
   1. 解决方法：使用 `exit` 退出 UEFI shell 后会进入 UEFI 界面，将「secure boot」关掉，保存并重启，即可正常启动 OpenWRT


