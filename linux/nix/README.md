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

不过使用 `pnpm i --global` 肯定会报错，因为全局环境是 readonly 的。

## Python 开发环境

而 Python 的开发环境实际比 JS/Go 等语言或要麻烦许多，因为它默认就往全局环境装软件，要往当前项目装，还必须得先创建虚拟环境（JS/Go 等语言里可没虚拟环境这种幺蛾子）。

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

根据错误信息，`pip install` 直接被 NixOS 禁用掉了，测试了 `pip install --user` 也同样被禁用。为了提升环境的可复现能力，Nix 把它们全部废掉了。
即使我们通过 `mkShell` 等方式创建一个新环境，这些命令照样会报错（猜测是 Nixpkgs 中的 pip 命令本身就被魔改了，只要是跑 `install` 等修改指令就直接嘎掉）。

但是很多项目的安装脚本都是基于 pip 的，这导致这些脚本都不能直接使用。

解决方案之一是改用 `venv` 虚拟环境：

> 但如果项目的脚本中本身仍要创建虚拟环境，还是会报错，python 不支持嵌套创建虚拟环境...

```shell
python -m venv ./env
source ./env/bin/activate
```

这样用 python 直接创建的 venv，对一些人而言可能还是没有安全感，仍然希望将这个虚拟环境也弄进 `/nix/store` 里使其不可变，通过 nix 直接安装 `requirements.txt` 或者 `poetry.toml` 中的依赖项。
这当然是可行的，有现成的 Nix 封装工具帮我们干这个活：

> 注意即使是在这俩环境中，直接跑 `pip install` 之类的安装命令仍然是会失败的！因为数据还是在 `/nix/store` 中，这类修改命令必须在 Nix 的构建阶段才能执行...

- [DavHau/mach-nix](https://github.com/DavHau/mach-nix)
- [poetry2nix](https://github.com/nix-community/poetry2nix)

这俩工具的好处是，能利用上 Nix Flakes 的锁机制来提升可复现能力，缺点是多了一层封装，底层变得更复杂了。
