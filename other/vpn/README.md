# VPN

## [wireguard vpn](https://github.com/linuxserver/docker-wireguard)

```shell
docker-compose -f docker-compose-wireguard.yml up -d
```

docker-wireguard 要求宿主机也是 debian/ubuntu 系统，否则可能会无法运行。
这是因为它需要编译 wireguard 并让它与宿主机内核正常交互。


## 其他 VPN

- [ipsec vpn](https://github.com/hwdsl2/docker-ipsec-vpn-server)
