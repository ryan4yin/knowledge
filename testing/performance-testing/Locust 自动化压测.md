# Locust 自动化压测

## 在 Kubernetes 上使用 Locust 进行自动化压测

使用当前文件夹下的 yaml 文件部署自动化压测

```shell
# 0. 在本地编写好 locustfile.py，保存到 k8s 中，供 locust 挂载
kubectl create configmap locustfile --from-file=locustfile.py=locustfile.py 

# 1. 部署 locust master
kubectl apply -f loucst-master.yaml
# 2. 部署 loucst slaves
kubectl apply -f loucst-slaves.yaml
```

然后就开始自动化压测了，可以修改 slaves 的 replicas 数量以增减 worker 数，记得同步修改 master 的 `--expect-workers`。
