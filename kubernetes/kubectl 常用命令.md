

```
# 查询某节点上的所有 pods
kubectl get pods --all-namespaces -o wide --field-selector spec.nodeName=<nodeName>

```