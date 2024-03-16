# [kyverno](https://github.com/kyverno/kyverno)

和 Open Policy Agent 相比，kyverno 更简单直观。

而且使用 kyverno，不仅仅能替代掉即将被淘汰的 PodSecurityPolicy，还有很多别的有趣的用处。

## 使用案例

- 自动添加默认的 SecurityContext、podAntiAffinity、禁用 default 名字空间、禁用镜像的 latest 标签等
- 跨名字空间同步 secrets

## 功能类似的其他软件

- https://github.com/datreeio/datree: 这是一个客户端的 yaml 检查工具，也可以实现禁用 default 名字空
  间、禁用镜像的 latest 标签等功能
  - 这个可以集成在 CI 里面，而 kyverno 可以作为「集群守门员」，双管齐下。

## 参考

- [Kyverno: The Swiss Army Knife of Kubernetes](https://neonmirrors.net/post/2021-01/kyverno-the-swiss-army-knife-of-kubernetes/)
