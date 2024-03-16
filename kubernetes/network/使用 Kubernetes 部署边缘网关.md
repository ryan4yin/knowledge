## 使用 Kubernetes 部署边缘网关

如我在 [Linux 504 超时丢包问题解决思路](/linux/性能优化/Linux%20504%20超时丢包问题解决思路.md) 所
言，Linux 的内核参数需要做一些自定义才能适用于边缘网关场景，尤其是 nf_conntrack 相关参数。

但是如果直接将 [Linux 参数调优](/linux/性能优化/参数调优.md) 放在节点的启动脚本（cloudinit）中执行的
话，对 nf_conntrack 部分的修改不会生效。其原因是 kube-proxy 会根据其 configmap 中的配置主动调整
nf_conntack 的部分参数，示例如下：

```shell
$ kubectl -n kube-system get cm kube-proxy-config -o yaml
...
...
    conntrack:
      maxPerCore: 32768
      min: 131072
      tcpCloseWaitTimeout: 1h0m0s
      tcpEstablishedTimeout: 24h0m0s
...
```

这个 configmap 的配置会在集群的所有节点上生效，但是我们只想修改边缘节点的相关参数，所以不建议修改其
内容。

为了避免此类问题，对节点内核参数的修改，更建议使用 Privileged Pod 来完成，示例如下：

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: "edgegateway-sysctl"
  namespace: "kube-system"
spec:
  template:
    metadata:
      labels:
        app: "edgegateway-sysctl"
    spec:
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
              - matchExpressions:
                  - key: my-nodegroup
                    operator: In
                    values:
                      - edge-gateway # only run on nodegroup: edge-gateway
      tolerations:
        - effect: NoSchedule
          key: xxx.com/edge-gateway # tolerate some taints exists on edge-gateway nodes
          operator: Exists
      containers:
        - name: "edgegateway-sysctl"
          image: "busybox:latest"
          resources:
            limits:
              cpu: "10m"
              memory: "8Mi"
            requests:
              cpu: "10m"
              memory: "8Mi"
          securityContext:
            privileged: true
          command:
            - "/bin/sh"
            - "-c"
            - |
              set -o errexit
              set -o xtrace

              # wait for 10s to make sure kube-proxy had updated nf_conntrack arguments successfully.
              sleep 10

              # update sysctl
              echo "
              # 发起连接时可用的端口范围
              net.ipv4.ip_local_port_range=1024 65535
              net.ipv4.tcp_tw_reuse=1
              net.ipv4.tcp_timestamps=1

              # 调大 nf_conntrack 连接跟踪表，避免溢出
              # 正常情况下 nf_conntrack_count 不应超过 nf_conntrack_buckets （hash 表容量）的 2/3，否则哈希表查询性能会剧烈下降
              # CONNTRACK_MAX 为 2097152，HASHSIZE 为 524288
              # 可计算出使用的最大内存为：(2097152 * 352 + 524288 * 8 ) / (1024 ** 2) = 708MiB
              net.netfilter.nf_conntrack_max=2097152
              net.netfilter.nf_conntrack_buckets=524288
              # 缩短 nf_conntrack 相关的超时时间
              net.netfilter.nf_conntrack_tcp_timeout_established=1800
              net.netfilter.nf_conntrack_icmp_timeout=10
              net.netfilter.nf_conntrack_tcp_timeout_syn_recv=10
              net.netfilter.nf_conntrack_tcp_timeout_syn_sent=10
              net.netfilter.nf_conntrack_tcp_timeout_fin_wait=30
              net.netfilter.nf_conntrack_tcp_timeout_time_wait=30
              " >> /etc/sysctl.conf
              # apply sysctl config
              while sysctl -p /etc/sysctl.conf
              do
                  echo "failed to run sysctl -p /etc/sysctl.conf, wait for 10s..."
                  sleep 10s
              done
```

## 参考

- <https://kubernetes.io/docs/reference/config-api/kube-proxy-config.v1alpha1/#kubeproxy-config-k8s-io-v1alpha1-KubeProxyConntrackConfiguration>
- <https://github.com/jetstack/navigator/blob/master/docs/quick-start/sysctl-daemonset.yaml>
