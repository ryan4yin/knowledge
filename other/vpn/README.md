# VPN

## [wireguard vpn](https://github.com/linuxserver/docker-wireguard)


**使用前提**：因为 wireguard 是一个内核模块，宿主机必须是 debian/ubuntu 系统，否则容器可能会无法运行。

启动命令：

```shell
docker-compose -f docker-compose-wireguard.yml up -d
```

## 使用客户端连接 WireGuard 服务器

Wireguard 官方客户端下载页面：https://www.wireguard.com/install/

wireguard 使用公私钥的方式进行认证，因此客户端和服务端都不需要设定任何密码/预共享密钥啥的。

手机连接方法：

通过 `docker-compose` 启动完成后，容器日志中会打印出二维码供手机端扫描。

PC 连接方法：

对于 PC 端，可以直接拷贝 `./config/peer1/peer1.conf`，导入到 wireguard 客户端中，即可完成连接。 

### Linux 通过命令行连接 WireGuard 服务器

Linux 各发行版根据前面提供的官方下载页面安装好 wireguard 后，就能获得一个命令行客户端 `wg-quick`

`wq-quick` 使用 `/etc/wireguard/<interface>.conf` 作为 vpn 的配置文件。

使用步骤如下：

1. 新建文件 `/etc/wireguard/wg0.conf`，内容拷贝自服务端的 `./config/peer1/peer1.conf`。
1. 运行命令 `wq-quick up wg0`，这会通过上面说的 `wg0.conf` 启动一个 vpn.


## 其他 VPN

- [ipsec vpn](https://github.com/hwdsl2/docker-ipsec-vpn-server)
