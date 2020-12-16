# Podman

## Podman 可以直接使用 kubernetes 配置

使用 podman 直接部署 k8s deployment:

```shell
podman play kube xxx.yaml
```

上述命令可以直接使用 kubernetes 的 deployemnt/job 创建容器。
不过 podman 没有控制器，因此只会创建 pod，而 deployment/job 的特殊参数会被忽略。

不得不说，真香!


