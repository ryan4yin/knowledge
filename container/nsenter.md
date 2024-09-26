### 9. 容器网络诊断 - nsenter

Docker 容器有自己的 namespace，直接通过宿主机的 ss 命令是查看不到容器的 socket 信息的。

比较直观的方法是直接通过 `docker exec` 在容器中通过 ss 命令。但是这要求容器中必须自带 ss
等程序，有的精简镜像可能不会自带它。

通过 `nsenter` 可以直接进入到容器的指定 namespace 中，这样就能直接查询容器网络相关的信息
了。

```shell
docker ps | grep xxx

echo CONTAINER=xxx  # 容器名称或 ID

# 1. 查询到容器对应的 pid
PID=$(docker inspect --format {{.State.Pid}} $CONTAINER)

# 2. nsenter 通过 pid 进入容器的 network namespace，执行 ss 查看 socket 信息
nsenter --target $PID --net ss -s

# 3. 进入容器的所有 ns，差不多等同于直接用 docker exec -it xxx bash 进入容器
nsenter -a -t $PID
```

`nsenter` 这个工具貌似是 docker 自带的或者是系统内置命令，只要装了 docker，ubuntu/centos
都可以直接使用这个命令。

> nsenter 是一个进入名字空间的工具，功能不仅仅局限在「网络诊断」，还有更多用法。

- [github - nsenter](https://github.com/jpetazzo/nsenter#how-do-i-use-nsenter)


