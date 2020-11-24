## Docker 数据持久化

Docker 持久化数据有两种方式：
1. 使用数据卷(volume)：更安全（只有挂载了该数据卷的容器可读写），和主机耦合度低,但是用起来总感觉隔着些东西...
      - 如果你要在多个容器间共享数据，那最佳选择是 volume
      - 通过使用 NFS 等 volume 驱动，还可以实现将数据保存到远程存储(NAS)中。
      - 但是缺点是，不熟悉 docker 的人基本不会使用 volume，它不够直观，可能一不小心跑个 `docker volume prune` 就把 volume 清掉了，而新来的运维小白还云里雾里。。
1. 文件夹映射(bind)：非常直观（一个很纯粹的文件夹，有权限的人都可以读写、查看），主机和容器可以很方便地交换数据（比如使用 rsync 定时备份），但是安全性差。
      - 非 root 容器使用文件夹映射时，一定会遇到权限问题，因为 [docker 默认创建的文件夹用户是 `root/root`](https://github.com/moby/moby/issues/2259)
      - 因为 bind(文件夹映射)很直观，我更多的时候都偏向于使用文件夹映射。
      - 启用 selinux 很可能导致 bind 权限问题，通常建议关闭复杂的 selinux...


volume 和 bind 的详细对比参见： 

1. [docker - volumes vs mount binds. what are the use cases?](https://serverfault.com/questions/996785/docker-volumes-vs-mount-binds-what-are-the-use-cases)
2. [docker data volume vs mounted host directory](https://stackoverflow.com/questions/34357252/docker-data-volume-vs-mounted-host-directory)
