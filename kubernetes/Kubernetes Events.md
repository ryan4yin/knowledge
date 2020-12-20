# Kubernetes Events


## 为什么我的 资源 Events 为 None？

Kubernetes 的 Events 由 kube-apiserver 管理，数据保存在 Etcd 中，而且默认只留存一个小时。

events 的留存时间可通过 kube-apiserver 的 `--event-ttl` 参数配置：

```shell
$ docker run --rm registry.cn-hangzhou.aliyuncs.com/google_containers/kube-apiserver:v1.18.0  kube-apiserver --help
......
Misc flags:
......
      --event-ttl duration                        Amount of time to retain events. (default 1h0m0s)
```

另外阿里云的 kubernetes 集群支持接入阿里云日志服务，将 Events 信息保存在日志服务中，实现长期的 Events 存储。

## 相关文档

- [Kubernetes可观察性：全方位事件监控 - 阿里云](https://developer.aliyun.com/article/745567)
- [Kubernetes events will disappear after one hour - Kubernetes Issue](https://github.com/kubernetes/kubernetes/issues/52521)
