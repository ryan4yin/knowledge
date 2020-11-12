# Redis

>注：这里使用 [bitnami/redis](https://hub.docker.com/r/bitnami/redis/) 而不是 docker 官方的 redis 镜像。因为 bitnami/redis 将很多参数封装成了环境变量，使用更方便。

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

参见 [bitnami/redis](https://hub.docker.com/r/bitnami/redis/) 文档。

## Linux 系统参数调整

Redis 启动时，可能会有 Warning 要求修改系统参数。

### 1. 打开资源描述符的最大数量与 TCP 最大连接数

>参数的修改可参考 [/operation-system/linux/README.md](/operation-system/linux/README.md)

Redis 需要打开大量的文件描述符，需要对系统的 ulimit/sysctl 参数做一些调整。
因为 docker 支持为容器设定 ulimit/sysctl，因此我将它直接写在 docker-compose.yml 里面了。

### 3. overcommit_memory

这个参数只能在宿主机上修改：

```
echo 1 > /proc/sys/vm/overcommit_memory  # 临时生效，既可改 /proc/xxx，也可通过 sysctl 命令修改内核参数 
echo "vm.overcommit_memory=1" >> /etc/sysctl.conf  # 重启后永久生效
```

### 4. transparent_hugepage

这个参数只能在宿主机上修改：

```
echo never > /sys/kernel/mm/transparent_hugepage/enabled  # 临时生效
```

暂时没找到在新系统的的有效方法，使系统重启也此参数的修改也能生效。。


