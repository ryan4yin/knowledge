# APISIX

APISIX 是一个国产的 API 网关，基于 Opentresty，其核心贡献者同时也是 Openresty 的核心贡献者。

它的性能要比 Kong 更优秀，有国内很多企业的落地案例，功能也很丰富，值得考虑。

## 部署到 Kubernetes

```shell
helm repo add apisix https://charts.apiseven.com
# 查看 apisix 版本号
helm search repo  apisix/apisix -l | head
# 下载并解压 chart，目的是方便 gitops 版本管理
helm pull apisix/apisix --untar --version 0.11.0
# 现在 copy 并自定义 helm chart 中的 values.yaml，新配置命名为 apisix-values.yaml
# 使用自定义配置安装 apisix
helm upgrade --install apisix ./apisix -f apisix-values.yaml
```

## 参考

- [APISIX 源码分析](https://shoujo.ink/2021/09/apisix-%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/)
