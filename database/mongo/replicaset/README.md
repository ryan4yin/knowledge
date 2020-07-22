# 一、副本集

副本集使用 Raft 算法选主（和 Etcd 一样），因此建议使用奇数个节点。下列演示使用三个节点。

使用配置文件 [docker-compose-3node.yml](./docker-compose-3node.yml) 即可启动一个三节点的 mongo 副本集。

启动命令：
```shell
mv docker-compose-3nodes.yml docker-compose.yml
docker-compose up -d
```

在容器 mongo1 中运行命令 `mongo --eval "rs.status()"` 就能查询到副本集的状态。
也可以通过 `mongo shell` 交互式地查询 mongo 副本集信息。

## 单节点副本集

测试环境下可以使用单节点副本集，它的 docker-compose 配置见 [docker-compose-1node.yml](./docker-compose-1node.yml)

启动命令：
```shell
mv docker-compose-1node.yml docker-compose.yml
docker-compose up -d
```

## 客户端

在只有一个副本集的情况下，客户端可以不指定副本集。


