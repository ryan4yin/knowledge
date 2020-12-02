# [OAM(Open Application Model)](https://github.com/oam-dev)

将应用配置拆分成三个关注点（关注点分离）：

1. 应用组件（Components）：面向应用开发人员的配置，剥离了所有运维配置。
2. 应用配置（Application Configuration）：平台无关的运维属性。
3. 应用运维特征（Traits）：平台相关的运维特征。

其中 1 和 2 是可以跨平台使用的，不局限于 k8s.

个人感觉 OAM 的主要应用场景在各大企业内部，开源项目主要还是会用 helm。
因为 OAM 标榜的运维特征与应用组件分离，对开源应用的意义不大，但是对企业内部成百上千的微服务部署而言，就意义重大了。


## [Kubevela](https://github.com/oam-dev/kubevela): 基于 OAM 构建的易用的 APP 平台

Kubevela 和 Knative 有点类似，但是貌似更简单。

## Kubernetes 标准实现：[CrossPlane](https://github.com/crossplane/crossplane)

待续
