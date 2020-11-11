# Redis

这里提供了两个 docker-compose 文件：

1. `docker-compose-cache.yml`: 将 redis 用作内存缓存服务器，效率高但是不保存数据。
2. `docker-compose-store.yml`: redis 启用数据持久化，效率低但是数据不会丢失。

启动停止方法（以缓存版为例）：

```
# 启动
docker-compose -f docker-compose-cache.yml up -d

# 停止 
docker-compose -f docker-compose-cache.yml down
```

## Redis 多副本

待研究

## 参考

- [Redis - bitnami](https://hub.docker.com/r/bitnami/redis/): 这个镜像比 docker 官方镜像使用更方便
