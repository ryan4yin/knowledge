# [Traefik](https://github.com/containous/traefik/) 配置

我接触过的三种用法：

1. Docker 单机方式：代理本机 Docker 上其他容器的流量，官方 sample 第一个就是。
1. File 方式：通过 yaml 文件配置路由策略，支持动态更新，不需要重启。
1. Kubernetes Ingress Controller 方式：用做 k8s 的入口网关，配置方式见 Kubernetes Ingress 官方文档。

## 流量属性

traefik 可以在第 4 层(tcp/udp)和第 5 层(http/tls/websocket/grpc)进行流量转发。

但是不支持 ftp/mysql/redis 等协议，这类协议当成第 4 层流量进行转发。设置这种转发意义不大，因为第 4 层只有两个可用信息：端口号和 IP，无法灵活地配置 LoadBalancer 等转发规则。个人感觉是弊大于利。


## 双向 TLS 认证（TLS）

配置方法参见 [file-mode/config/dynamic.yml](./file-mode/config/dynamic.yml)。

使用 curl 测试 mTLS:

```shell
# 进入到证书存放文件夹 certs
cd certs
# 验证双向 TLS 认证，-v 选项查看详细的 HTTP 请求过程
## 1. 使用客户端证书
curl -v --cacert ca.crt --cert ./client.crt --key client.key --tls-max 1.2 https://traefik.xxx.local
## 2. 不使用客户端证书，会报错： SSL peer cannot verify your certificate.
curl -v --cacert ca.crt --tls-max 1.2 https://traefik.xxx.local
```

使用 python requests 测试 mTLS:

```python
import requests

session = requests.Session()
# 设置用于验证服务端证书的证书链
session.verify = "./ca.crt"
# 设置客户端证书与密钥
session.cert = ("./client.crt", "./client.key")

url = "https://traefik.xxx.local"
for i in range(30):
    # 连续请求 30 次
    resp = session.get(url)
    print(resp.status_code, resp.headers)
```
