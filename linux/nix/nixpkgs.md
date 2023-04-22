# nixpkgs 使用

## 安装

>https://mirrors.bfsu.edu.cn/help/nix/

可以使用 tuna/bfsu 的镜像源加速安装，多用户安装命令：

```shell
sh <(curl https://mirrors.bfsu.edu.cn/nix/latest/install) --daemon
```

## cache 镜像

cache 镜像同样可以使用 tuna/bfsu 镜像源加速，nixpkgs 多用户安装时修改 `/etc/nix/nix.conf` 添加如下内容：

```conf
substituters = https://mirrors.bfsu.edu.cn/nix-channels/store https://cache.nixos.org/
```

改完后要重启 nix-daemon 服务才能生效，对于 nix-darwin，可以使用如下命令重启：

```shell
sudo launchctl stop org.nixos.nix-daemon
sudo launchctl start org.nixos.nix-daemon
```

对于 nixos 等基于 systemd 的 linux 系统，可以使用如下命令重启：

```shell
sudo systemctl restart nix-daemon
```

## nixpkgss channel 镜像

>https://nixos.wiki/wiki/Nix_channels

>https://mirrors.bfsu.edu.cn/help/nix-channels/

使用 bfsu 镜像源加速 nixpkgss nixpkgss-unstable channel 的方法如下：

```shell
nix-channel --add https://mirrors.bfsu.edu.cn/nix-channels/nixpkgss-unstable nixpkgss
nix-channel --list
nix-channel --update
```
