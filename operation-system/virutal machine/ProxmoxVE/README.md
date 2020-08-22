# [Proxmox Virtual Environment](https://pve.proxmox.com/)

PVE 是一个开源免费，订阅收费的服务器虚拟化系统，基于 QEMU/KVM.

和 ESXi 相比，它的优势有：

1. 底层是 QEMU/KVM，这是目前最主流的服务器虚拟化方案。
2. 提供一套方便的 CLI 工具，以及 RESTful API。不论是 CLI、HTTP API 还是 [Python SDK](https://github.com/proxmoxer/proxmoxer)，PVE 都比 ESXi 要好用很多！

缺点在于，PVE 的 WebUI 功能不全，有些功能必须通过命令行才能实现。（这和路由器类似，高级功能只有 CLI 支持）
