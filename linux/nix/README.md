# Nix

笔记已迁移至: <博客 <https://thiscute.world/posts/nixos-and-flake-basics/>>

我的 nix 配置：[ryan4yin/nix-config](https://github.com/ryan4yin/nix-config)

## disk encryption

Physicial disk may borked, and you need to repair it by send it back to the manufacturer. In this case, you may have some sensitive data on it and you would suffer from data leakage, because the manufacturer may not be trusted, and they can read data directly from the disk.

so the best way to protect your data is to encrypt the disk all the time, you can encrypt the disk with a password to protect your data.

https://gist.github.com/ladinu/bfebdd90a5afd45dec811296016b2a3f

https://www.reddit.com/r/NixOS/comments/xrgszw/nixos_full_disk_encryption_with_tpm_and_secure/

https://github.com/NixOS/nixpkgs/blob/nixos-23.05/nixos/doc/manual/configuration/luks-file-systems.section.md

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
