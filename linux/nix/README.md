# Nix

笔记已迁移至: <博客 <https://thiscute.world/posts/nixos-and-flake-basics/>>

我的 nix 配置：[ryan4yin/nix-config](https://github.com/ryan4yin/nix-config)

## disk encryption

Physicial disk may borked, and you need to repair it by send it back to the manufacturer. In this case, you may have some sensitive data on it and you would suffer from data leakage, because the manufacturer may not be trusted, and they can read data directly from the disk.

so the best way to protect your data is to encrypt the disk all the time, you can encrypt the disk with a password to protect your data.

https://gist.github.com/ladinu/bfebdd90a5afd45dec811296016b2a3f

https://www.reddit.com/r/NixOS/comments/xrgszw/nixos_full_disk_encryption_with_tpm_and_secure/

https://github.com/NixOS/nixpkgs/blob/nixos-23.05/nixos/doc/manual/configuration/luks-file-systems.section.md

# 开发环境搭建

NodeJS 的依赖是下载到当前项目文件夹中的 `node_modules`，在 NixOS 上进行相关开发非常舒适，`pnpm i` 等命令都能正常运行。

不过使用 `pnpm i --global` 肯定会报错，因为全局环境是 readonly 的。

