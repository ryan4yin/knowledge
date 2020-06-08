# 一、副本集

副本集使用 Raft 算法选主（和 Etcd 一样），因此建议使用奇数个节点。下列演示使用三个节点。

1. 启动：`docker-compose up`
1. 初始化副本集：在任意 mongo 容器中运行如下命令：
    ```shell
    mongo --eval 'rs.initiate( { _id : "rs0",members: [{ _id: 0, host: "mongo1.db.local:27017" },{ _id: 1, host: "mongo2.db.local:27018" },{ _id: 2, host: "mongo3.db.local:27019" }   ]})'
    ```

注意：上述命令中的 `mongox.db.local` 必须是正确的可使用的域名！并且客户端能正常解析！
如果没有私有 DNS 服务器/域名，建议将这三个域名修改成 `IP` 地址！

>这里不使用 docker 内部 DNS 名称的原因是，外部客户端无法解析该域名。这将导致外部客户端无法使用此 Mongo 副本集。

## 单节点副本集

测试环境下可以使用单节点副本集，方法如下：

1. 修改 `docker-compose.yml`，删除掉 `mong2` 和 `mong3` 的配置，然后启动容器。
2. 在 `mongo1` 中运行如下命令，完成副本集的初始化：
    ```shell
    mongo --eval 'rs.initiate( { _id : "rs0",members: [{ _id: 0, host: "mongo1.db.local:27017" }] })'
    ```


## 客户端

在只有一个副本集的情况下，客户端可以不指定副本集。（不保证正确）


