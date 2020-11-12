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

## Linux 系统参数调整

Redis 启动时，可能会有 Warning 要求修改系统参数。

### 1. 最大打开的资源描述符数量

Redis 需要打开大量的文件描述符，需要对系统的 ulimit 参数做一些调整。
这部分内容参见 [/operation-system/linux/README.md](/operation-system/linux/README.md)

### 2. 最大连接数

```
sysctl -w net.core.somaxconn=20000  # 临时生效 
echo "net.core.somaxconn = 20000" > /etc/sysctl.conf  # 重启后永久生效
```

### 3. overcommit_memory

```
echo 1 > /proc/sys/vm/overcommit_memory  # 临时生效，既可改 /proc/xxx，也可通过 sysctl 命令修改内核参数 
echo "vm.overcommit_memory=1" >> /etc/sysctl.conf  # 重启后永久生效
```

### 4. transparent_hugepage

```
echo never > /sys/kernel/mm/transparent_hugepage/enabled  # 临时生效
```

暂时没找到在新系统的的有效方法，使系统重启也此参数的修改也能生效。。

## 参考

- [Redis - bitnami](https://hub.docker.com/r/bitnami/redis/): 这个镜像比 docker 官方镜像使用更方便
