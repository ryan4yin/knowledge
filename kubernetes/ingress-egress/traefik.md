# Traefik Ingress

部署流程：

```shell
# 添加　chart 仓库
helm repo add traefik https://helm.traefik.io/traefik
# 查看历史版本
helm search repo traefik/traefik -l | head
# 下载并解压 chart，目的是方便 gitops 版本管理
helm pull traefik/traefik  --untar --version 2.15.1

# 查看生成出的 kubernetes yaml 内容
helm template ./traefik --namespace ingress \
  -f traefik-values.yaml > traefik-all.yaml

# 安装或更新
kubectl create namespace ingress
helm upgrade --install traefik --namespace ingress \
  -f traefik-values.yaml ./traefik
```

具体使用，参见官方文档。。。
