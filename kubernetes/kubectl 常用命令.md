
## 查询

```shell
# 查询某节点上的所有 pods
kubectl get pods --all-namespaces -o wide --field-selector spec.nodeName=<nodeName>

# 各可用区的节点数量统计
# uniq -c 按出现次数(count)进行统计
# sort -nr  按数值(number)比较排序并逆序(reverse)输出结果
kubectl get nodes --label-columns "topology.kubernetes.io/zone" --no-headers | awk '{print $6}' | uniq -c | sort -nr

# 各实例类型的节点数量统计
kubectl get nodes --label-columns "node.kubernetes.io/instance-type" --no-headers | awk '{print $6}' | sort | uniq -c | sort -nr

kubectl get nodes --label-columns "topology.kubernetes.io/zone,node.kubernetes.io/instance-type" --no-headers | awk '{print $6,$7}' | sort | uniq -c | sort -nr

```

```shell
# get replicas
kubectl -n prod get deploy -o jsonpath="{range .items[*]}'{.metadata.name}': {.spec.replicas}{'\n'}{end}" > deployment_replicas.yaml

# get replicas - current
kubectl -n prod get deploy -o jsonpath="{range .items[*]}'{.metadata.name}': {'\n'}  replicas: {.spec.replicas}{'\n'}  ready: {.status.readyReplicas}{'\n'}{end}" > deployment_replicas_ready.yaml

# get images
kubectl -n staging get deploy -o jsonpath="{range .items[*]}'{.metadata.name}': {.spec.template.spec.containers[0].image}{'\n'}{end}" > deployment_images.yaml
```

查询所有 api 资源:

```
kubectl api-resources --verbs=list
```

## 回滚 deployment/daemonset/statefulset

注意 configmap/secrets/rolebinding 等其他配置是没有历史版本管理的！回滚 pod 配置前请先确认是否有用到这些配置，否则可能会导致问题。
```
# 回滚 deployments
## 查询历史版本
kubectl rollout history deployment <deployment-name>
## 查看历史版本的详细信息
kubectl rollout history deployment <deployment-name> --revision=1
## 回滚到某个版本
kubectl rollout undo deployment.v1.apps/<deployment-name> -n prod --to-revision=7
## 回退到上一个版本
kubectl rollout undo deployment.v1.apps/<deployment-name> -n prod

# 回滚 daemonset
## 查询历史版本
kubectl rollout history daemonset <daemonset-name>
## 查看历史版本的详细信息
kubectl rollout history daemonset <daemonset-name> --revision=1
## 回退到某个历史版本
kubectl rollout undo daemonset.v1.apps/<daemonset-name> -n prod --to-revision=7
## 回退到上一个版本
kubectl rollout undo daemonset.v1.apps/<daemonset-name> -n prod
```


## 删除

删除所有 crash 的 Pod(在流量压力大的时候，快速启动所有 pod，分担请求压力，避免起一个 pod 被打死一个（预热阶段被打死了），导致全都启动不起来):
```
kubectl delete pod `kubectl get pod -n prod | grep xxx | awk '$3 == "CrashLoopBackOff" {print $1}'`
```
