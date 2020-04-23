## Traefik Docker 模式

通过 `docker-compose up -d` 启动 traefik 后，可以通过 `http://traefik.local` 访问 traefik.dashboard（需要自行设置内网 DNS 解析，或者修改本机 hosts 文件）。

将本机的其他 docker 容器的 traefik 配置写在 docker labels 中，traefik 就能自动发现它并动态更新路由规则。

示例应用的 docker-compose 配置:

```yaml
version: "3"
services:
  my-service:
    container_name: my-container
    image: my-image
    labels:
    - traefik.http.routers.my-container.rule=Host(`my-service.local`)
    # 如果容器 expose 了多个端口，或者没有暴露端口，就需要通过如下参数去告诉 traefik 将流量路由到哪个端口
    # - traefik.http.services.my-service.loadbalancer.server.port=<my-port>
    restart: always
```

另外安全起见，也可以通过 docker-compose 的 `networks` 属性使用独立的虚拟网络。（默认情况下，所有容器都自动连接到 default 网桥，因此 traefik 能直接访问其他容器）
不过这样就需要在 traefik 的 docker-compose.yml 中指定加入这个虚拟网络，否则 traefik 就无法将流量路由到该网络中去。

详见 [Traefik & Docker](https://docs.traefik.io/providers/docker/)

