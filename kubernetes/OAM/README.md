# [OAM(Open Application Model)](https://github.com/oam-dev/spec)

将应用配置拆分成三个关注点（关注点分离）：

1. 应用组件（Components）：面向应用开发人员的配置，剥离了所有运维配置。
2. 应用配置（Application Configuration）：平台无关的运维属性。
3. 应用运维特征（Traits）：平台相关的运维特征。

其中 1 和 2 是可以跨平台使用的，不局限于 k8s.


## Kubernetes 标准实现：[CrossPlane](https://github.com/crossplane/crossplane)

待续
