# Linux LVM 逻辑卷管理

LVM 通过在物理分区上，虚拟了一个逻辑层，来实现灵活的磁盘分配。
它灵活性的最大体现在于：**逻辑卷可以将多个分区、甚至多个物理硬盘，虚拟成一个逻辑卷来使用。**

### 1. LVM 扩容

- [Linux 挂载新硬盘/LVM 逻辑卷扩容](https://www.cnblogs.com/kirito-c/p/11938024.html)

### 2. LVM 缩容，去除物理磁盘

注意！缩容貌似是很危险的操作，很可能导致数据丢失！
需要提前将需要移除的硬盘上的数据迁移走，目前还没搞清楚怎么迁移。。

我上次缩容根文件系统，直接导致系统核心文件损坏，整个虚拟机崩溃。。。

## 相关文档

- [逻辑卷管理器管理 - RedHat Docs](https://access.redhat.com/documentation/zh-cn/red_hat_enterprise_linux/7/html/logical_volume_manager_administration/lvm_overview)