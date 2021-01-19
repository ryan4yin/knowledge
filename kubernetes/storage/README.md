# 分布式数据存储

kubernetes 上的分布式数据存储方案,比较被看好的有：

1. rook: 在 kubernetes 上部署 ceph/edgefs 等分布式文件系统，最成熟的方案是 ceph
2. minio: kubernetes 上的高性能对象存储，貌似非常流行。使用维护都很简单，社区也很活跃。

上述 storage on kubernetes 方案的可靠性还有待考察。
目前云上存储首选各云厂商提供的存储方案，自建存储建议直接连接集群外部的 Ceph/GlusterFS/OSS。

对性能要求不高，或者需要数据共享的场景下，可以考虑使用 NFS/iSCSI 远程存储做为 kubernetes 的存储方案。
