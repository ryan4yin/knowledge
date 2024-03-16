# Kubernetes 网络插件

Kubernetes 社区有众多的网络插件可供选择，其中比较著名，用的人也比较多个有如下几个：

2. [Flannel](https://github.com/coreos/flannel): 基于 Linux TUN/TAP 技术，使用 UDP 封装 IP 包来创建
   overlay 网络。因此性能会差一些，但是它部署起来最简单。
3. [Calico](https://github.com/projectcalico/calico): calico 支持 overlay （四层网络虚拟）或者
   non-overlay 两种技术，其中 non-overlay 技术通过 BGP 直接利用了外部网络，不需要虚拟网络，因此性能
   比 flannel 强，但也更复杂。
4. [Weave](https://github.com/weaveworks/weave): weave 也是一个 overlay 网络，但是数据不存 etcd 里
   面，它是完全去中心化的。
5. [Cilium](https://github.com/cilium/cilium): Cilium 是一个基于 eBPF 和 XDP 的高性能容器网络方案，
   工作在三/四层。因为使用了 eBPF，它的性能比 flannel/calico 都要强数倍。国内携程就使用了 Cilium+BGP
   的网络方案。

初学者接触的最多的，应该是 calico/flannel，而最有前景的应该是 cilium. 但是目前 calico 好像也在添加
eBPF 支持，cilium 也提供了 IPSec 透明加密的功能，各大网络插件的功能感觉在渐渐同质化。

## 学习路径

待续

## 相关文档

- [CNI 介绍 - 容器网络 - CDN Handbook](https://sdn.feisky.xyz/rong-qi-wang-luo/index/index/index)

视频:

- [Tutorial: Communication Is Key - Understanding Kubernetes Networking - Jeff Poole, Vivint Smart Home](https://www.youtube.com/watch?v=InZVNuKY5GY&list=PLj6h78yzYM2O1wlsM-Ma-RYhfT5LKq0XC&index=15)
- [eBPF and Kubernetes: Little Helper Minions for Scaling Microservices - Daniel Borkmann, Cilium](https://www.youtube.com/watch?v=99jUcLt3rSk&list=PLj6h78yzYM2O1wlsM-Ma-RYhfT5LKq0XC&index=74)
