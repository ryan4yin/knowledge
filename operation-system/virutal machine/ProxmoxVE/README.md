# [Proxmox Virtual Environment](https://pve.proxmox.com/)

PVE 是一个开源免费，订阅收费的服务器虚拟化系统，基于 QEMU/KVM.

和 ESXi 相比，它的优势有：

1. PVE 底层是 QEMU/KVM，存储方案也是 Ceph/iSCSI/NFS/LVM 这些都是使用很广泛的技术，学会了还可以应用在别的地方。
2. 提供一套方便的 CLI 工具，以及 RESTful API。不论是 CLI、HTTP API 还是 [Python SDK](https://github.com/proxmoxer/proxmoxer)，PVE 都比 ESXi 要好用很多！
3. 文档齐全，而且很接地气，还包含许多 QEMU/KVM/CEPH 等开源技术的内容。 反观 VMware 的文档，真的是写得烂得一批。

缺点在于，PVE 的 WebUI 功能不全，有些功能必须通过命令行才能实现。（这和路由器类似，高级功能只有 CLI 支持）
