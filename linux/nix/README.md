# Nix

笔记已迁移至: <博客 <https://thiscute.world/posts/nixos-and-flake-basics/>>

我的 nix 配置：[ryan4yin/nix-config](https://github.com/ryan4yin/nix-config)

## disk encryption

<https://github.com/ryan4yin/nix-config/tree/nixos-install>

## devbox 调研

优点：基本等同于 Nix 的优点，外加的一条是它多了一层抽象，使得普通用户不需要理解底层 Nix 的细节。

缺点：

1. 只能使 Nix 生态中的东西可复用，因此你如果需要使用非 Nix 生态中的东西，就需要自己写 flake，这就需要你理解 Nix 的细节了。
    1. 抽象泄漏，不过这个可以由基础设施团队 cover 住，开发者就可以专注于业务了。
2. 互联网企业大都用 macOS，但是 macOS 下的 devbox，实际跟线上 Linux 环境是有较大区别的，这会导致 devbox 的开发环境与线上环境不一致。
    1. 不同的 OS、不同的 CPU 架构，对应的 Nix 打包代码、构建工具链都可能会不一样，这没法避免。
    2. 比较好的解决方案仍然是容器化，但是容器化的话，就跟 devcontainer 差不多了。虽然也比纯 devcontainer 可复现性更强，但原生的开发体验就没了。


## 软件打包

1. nativeBuildInputs: 本地环境（编译环境）的构建依赖，仅在编译期需要，软件架构也与构建平台一致
3. buildInputs: 运行环境的运行依赖，软件架构与目标运行环境一致

### Python 应用


TODO

## 在 NixOS 上运行高可用 Kubernetes 集群

https://github.com/NixOS/nixpkgs/tree/nixos-23.05/nixos/modules/services/cluster/kubernetes

https://nixos.org/manual/nixos/stable/index.html#sec-kubernetes

https://nixos.wiki/wiki/Kubernetes

