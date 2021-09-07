
## 一、控制层（Control Plane, Master）

1. etcd: 有状态，etcd 集群会自己选举出 leader
    - k8s 集群的唯一存储组件，所有的集群元信息都保存在这里面。
1. apiserver: 无状态应用
    - 只干一件事：提供对 Etcd 的 CURD 操作。另外提供了 watch 方式通知客户端资源的变更。
    - 唯一直接与 etcd 交互的组件，其他所有组件都通过它提供的 restful api 读写集群元数据。
    - api server 本身会对 rest api 请求进行数据校验（确认数据合法）、身份认证与授权、处理乐观锁。
1. kube-controller manager: 有状态，会通过 etcd 选举出 leader
    - 
1. kube-scheduler: 有状态，会通过 etcd 选举出 leader

注意上述几个组件的 leader 之间是相互独立的，不同组件的 leader 完全可以在不同机器上。各组件也可以进行单独部署/扩容。

## 工作节点 Worker Node

1. kubelet: 管理 kubernetes Pod
1. kube-proxy: 管理 Kubernetes 网络
2. apiserver 负载均衡(nginx proxy): kubelet 通过它访问 apiserver，以实现 apiserver 的高可用。
    - 每个节点都有自己的 apiserver 负载均衡，非中心化，以保证高可用。
    - 云厂商可能有不同的实现方式，比如依赖自己的云产品：负载均衡。

### 相关问题

- kube-proxy 短时间不可用，会有什么影响？
  - EKS 的 kube-proxy 是使用 daemonset 部署的，如果某节点上的 kube-proxy pod 被 kill 掉，在新 pod 未就绪前，会发生什么？
- 同理，网络插件也基本都有 node agent，如果该 agent 短时间不可用，会发生啥？

