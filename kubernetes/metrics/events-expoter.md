# Events Expoter 事件导出工具

K8s Events 默认只保留 1h，我们为了实现基于 Events 的分析、告警功能、或者长期存储，都需要将 Events 导
出到外部存储，这需要借助一个 events expoter 组件。

社区有好几个实现，目前还在维护的有这几个：

- [opsgenie/kubernetes-event-exporter](https://github.com/opsgenie/kubernetes-event-exporter):
  atlassian 开源的项目，Jira/Confluence 都是这家公司搞的，感觉质量还是有保证的。
- [AliyunContainerService/kube-eventer](https://github.com/AliyunContainerService/kube-eventer): 国
  内阿里云开源的项目，很担心能活多久...
- [kubesphere/kube-events](https://github.com/kubesphere/kube-events): 国内青云开源的一个项目，看介
  绍功能也很齐全，不过 stars 比较少
