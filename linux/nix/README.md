# Nix

笔记已迁移至博客 <https://thiscute.world/posts/nixos-and-flake-basics/>

我的 nix 配置：[ryan4yin/nix-config](https://github.com/ryan4yin/nix-config)

## disk encryption

Physicial disk may borked, and you need to repair it by send it back to the manufacturer. In this case, you may have some sensitive data on it and you would suffer from data leakage, because the manufacturer may not be trusted, and they can read data directly from the disk.

so the best way to protect your data is to encrypt the disk all the time, you can encrypt the disk with a password to protect your data.

https://gist.github.com/ladinu/bfebdd90a5afd45dec811296016b2a3f

https://www.reddit.com/r/NixOS/comments/xrgszw/nixos_full_disk_encryption_with_tpm_and_secure/

https://github.com/NixOS/nixpkgs/blob/nixos-23.05/nixos/doc/manual/configuration/luks-file-systems.section.md

# 开发环境搭建

NodeJS 的依赖是下载到当前项目文件夹中的 `node_modules`，在 NixOS 上进行相关开发非常舒适，`pnpm i` 等命令都能正常运行。

## Python 开发环境

Python 的 pip 默认会将软件安装到全局，在 NixOS 中 `pip install` 会直接报错：

```shell
› pip install -r requirements.txt
error: externally-managed-environment

× This environment is externally managed
╰─> This command has been disabled as it tries to modify the immutable
    `/nix/store` filesystem.

    To use Python with Nix and nixpkgs, have a look at the online documentation:
    <https://nixos.org/manual/nixpkgs/stable/#python>.

note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages.
hint: See PEP 668 for the detailed specification.
```

根据错误信息，`pip install` 直接被 NixOS 禁用掉了，而且即使改用 `pip install --user` 也同样不行。

但是很多项目的安装脚本都是基于 pip 的，这导致这些脚本都不能直接使用。

解决方案之一是改用 `venv` 虚拟环境：

```shell
python -m venv ./env
source ./env/bin/activate
```

不过在 NixOS 上，更好的方案当然是使用 `nix develop` 跟 mkShell，在它创建的虚拟环境中，`pip install` 是能正常使用的。
