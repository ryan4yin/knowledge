# [Helm](https://github.com/helm/helm) - Kubernetes 包管理器

Helm 对运维人员而言，有两种用途：

1. 使用别的项目提供的 helm chart，进行快捷部署。云原生社区 90% 以上的项目，都有提供官方的 helm
   chart.
2. 用于方便快捷地渲染出自家微服务/应用的 yaml 配置。

## 使用社区提供的 helm chart 进行应用部署

这个没啥好说的，直接 `helm install` 就好。

需要注意的是，通常我们在部署时都需要自定义一些参数，推荐编写一个 `custom-values.yaml`，然后通过
`helm install -f custom-values.yaml` 进行部署。

## helm chart + gitops

自定义 helm chart 通常的使用流程，和用社区的 chart 没啥区别。

需要注意的是，如果你希望先将 helm chart 渲染成 yaml 文件，然后通过 gitops 工具进行部署，可以使用 如
下 helm 命令：

```
helm template <chart-dir-path> --output-dir <output-dir>
```

此命令会在 `<output-dir>` 下保存所有的渲染结果，而且文件的目录结构和源 helm chart 完全一致。

问：argo-cd 等工具本身就支持 helm chart，为何还需要提前将 chart 渲染成 yaml 呢？

答：为了保证所见即所得，我们选择在 git 仓库中保存 chart 渲染结果。helm chart 的可读性不佳，而且也要
考虑到并不是所有开发/运维人员，都看得懂 helm chart 的语法。

## 其他

常用命令：

```shell
# 列出所有名字空间中安装的 helm charts
helm list --all-namespaces
# 缩写形式
helm list -A
```
