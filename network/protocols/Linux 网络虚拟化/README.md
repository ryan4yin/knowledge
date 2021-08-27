# 网络虚拟化

- vlan 是链路层（二层）虚拟技术
- vxlan 是传输层（四层，UDP）虚拟化技术
- geneve
- ipip
- macvlan
- ipvlan


## overlay 与 underlay

在现有的物理网络之上构建的虚拟网络，被称为 overlay 网络。
而物理网络，被称为 underlay 网络。

vlan 与 vxlan 都是 overlay 网络。

## 参考

- [VXLAN vs VLAN](https://zhuanlan.zhihu.com/p/36165475)
