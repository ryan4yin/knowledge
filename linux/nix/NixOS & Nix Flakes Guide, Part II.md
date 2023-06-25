## Nix Modules System

- [Nix modules: Improving Nix's discoverability and usability ](https://cfp.nixcon.org/nixcon2020/talk/K89WJY/)

建议一读模块系统的完整实现：

https://github.com/NixOS/nixpkgs/blob/nixos-23.05/lib/modules.nix

### 模块系统的特殊参数

> https://github.com/NixOS/nixpkgs/blob/nixos-unstable/doc/module-system/module-system.chapter.md

```nix

_module.args: https://github.com/NixOS/nixpkgs/blob/nixos-23.05/lib/modules.nix#L123

```

## 自定义 Linux 内核

> https://github.com/NixOS/nixpkgs/blob/nixos-23.05/nixos/doc/manual/configuration/linux-kernel.chapter.md?plain=1#L122

在将 NixOS 移植到新的硬件平台时，可能需要自定义 Linux 内核。

先看下 buildLinux 函数，这玩意儿也没任何文档：

```
nix-repl> buildLinux
«lambda @ /nix/var/nix/profiles/per-user/root/channels/nixos/pkgs/top-level/linux-kernels.nix:632:16»

nix-repl> linuxManualConfig
«lambda @ /nix/var/nix/profiles/per-user/root/channels/nixos/lib/customisation.nix:70:24»

nix-repl> ubootTools
«derivation /nix/store/fias8r1np8zsws9hk5g78xm6vc5kv67m-uboot-tools-only_defconfig-2022.10.drv»
```

好的 buildLinux 的定义是在这里，看下内容：

> https://github.com/NixOS/nixpkgs/blob/master/pkgs/top-level/linux-kernels.nix#L684

```nix

  buildLinux = attrs: callPackage ../os-specific/linux/kernel/generic.nix attrs;

```

这样就定位到了实际的代码逻辑： https://github.com/NixOS/nixpkgs/blob/master/pkgs/os-specific/linux/kernel/generic.nix

同理现在看看 linuxManualConfig 的定义：发现它居然是 `mkOverride` 函数，直接断了线索。最后来是全局搜索 + 肉眼跟踪，定位到它实际定义在:

https://github.com/NixOS/nixpkgs/blob/master/pkgs/os-specific/linux/kernel/manual-config.nix#L19

### 自定义 GCC/Clang

1. https://nixos.wiki/wiki/Using_Clang_instead_of_GCC
   1. `localSystem` 跟 `crossSystem` 还有个 `useLLVM` 属性可以设定为 true，不过不知道 work 不 work
   2. https://github.com/NixOS/nixpkgs/issues/225074
2. https://nixos.wiki/wiki/C#Use_a_different_compiler_version

> need convert to the flake style

```nix
(import <nixpkgs> { overlays = [(self: super: { gcc = self.gcc10; })]; }).stdenv.cc
```

```nix
(mkShell.override { stdenv = gcc10Stdenv; }) {
  …
}
```

检查了下发现 pkgs 中确实存在 `gcc10Stdenv` `gcc11Stdenv` `gcc12Stdenv` `gcc13Stdenv` 这几个，分别指向不同的 derivation.

## disk encryption

Physicial disk may borked, and you need to repair it by send it back to the manufacturer. In this case, you may have some sensitive data on it and you would suffer from data leakage, because the manufacturer may not be trusted, and they can read data directly from the disk.

so the best way to protect your data is to encrypt the disk all the time, you can encrypt the disk with a password to protect your data.

https://gist.github.com/ladinu/bfebdd90a5afd45dec811296016b2a3f

https://www.reddit.com/r/NixOS/comments/xrgszw/nixos_full_disk_encryption_with_tpm_and_secure/

https://github.com/NixOS/nixpkgs/blob/nixos-23.05/nixos/doc/manual/configuration/luks-file-systems.section.md

## RISC-V/ARM64 building

这种构建场景下，官方的缓存经常会因为 gcc / kernel 等版本不匹配而失效，所以需要自己本地构建。

加速方法：

1. 搭建自己的缓存库
2. 分布式构建

## 将 gcc 工具链替换为 T-Head 官方的

最近遇到的各种问题，很多都是因为使用了 NixOS 的标准工具链导致的，到目前也没解决。

通过 devShell 创建了一个 FHS 环境，用 T-Head 提供的工具链编译，发现完全不报错，但切换回 NixOS 的工具链就会有错误。

所以还是决定直接使用 T-Head 提供的工具链，这样也能保证与官方的开发环境一致。

那么现在的问题就是，如何替换掉 nixpkgs 中的交叉编译工具链？

这里找到个配置 https://github.com/tattvam/nix-polarfire/blob/master/icicle-kit/default.nix

```nix
with import <nixpkgs> {
  crossSystem = {
    config = "riscv64-unknown-linux-gnu";
  };
  overlays = [ (self: super: { gcc = self.gcc11; }) ];
};
rec {

  uboot-polarfire-icicle-kit = callPackage ./uboot { defconfig = "microchip_mpfs_icicle"; };
  linux-polarfire-icicle-kit = callPackage ./linux { };
}
```

通过 `nix repl` 验证了确实是 work 的：

```shell
› nix repl -f '<nixpkgs>'
Welcome to Nix 2.13.3. Type :? for help.

Loading installable ''...
Added 17755 variables.

# 通过 overlays 替换掉 gcc
nix-repl> a = import <nixpkgs> {   crossSystem = {     config = "riscv64-unknown-linux-gnu";   };   overlays = [ (self: super: { gcc = self.gcc12; }) ]; }

# 查看下 gcc 版本，确实改成 12.2 了
nix-repl> a.pkgsCross.riscv64.stdenv.cc
«derivation /nix/store/jjvvwnf3hzk71p65x1n8bah3hrs08bpf-riscv64-unknown-linux-gnu-stage-final-gcc-wrapper-12.2.0.drv»

# 再看下未修改的 gcc 版本，还是 11.3
nix-repl> pkgs.pkgsCross.riscv64.stdenv.cc
«derivation /nix/store/pq3g0wq3yfc4hqrikr03ixmhqxbh35q7-riscv64-unknown-linux-gnu-stage-final-gcc-wrapper-11.3.0.drv»
```

那么如果我们要将 T-Head 的工具链使用上述 overlays 方式替换进来，现在得考虑下如何将 T-Head 工具链打包成一个 derivation。

T-Head 的工具链用的是 gcc 10，查看下 gcc 10 的 derivation：

https://github.com/NixOS/nixpkgs/blob/22.11/pkgs/development/compilers/gcc/10/default.nix

以及 T-Head 开源的修改版 GCC 10::

https://github.com/T-head-Semi/gcc/tree/xuantie-gcc-10.4.0

刚好两个连版本号都一样，那么直接 override 掉 src 跟 version 咋样？看看效果：

```nix
{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-22.11";

    # https://github.com/T-head-Semi/gcc/tree/xuantie-gcc-10.4.0
    thead-gcc = {
      url = "github:T-head-Semi/gcc/xuantie-gcc-10.4.0";
      flake = false;
    };
  };

  outputs = inputs@{ self, nixpkgs, thead-gcc, ... }:
  let
    pkgsKernel = import nixpkgs {
      localSystem = "x86_64-linux";
      crossSystem = {
        config = "riscv64-unknown-linux-gnu";
      };
      overlays = [
        (self: super: {
          # NixOS 22.11 uses gcc 10.4.0, the same as thead-gcc, see:
          #   https://github.com/NixOS/nixpkgs/blob/nixos-22.11/pkgs/development/compilers/gcc/10/default.nix
          gcc = super.gcc10.overrideAttrs  (finalAttrs: previousAttrs: {
            version = "10.4.0";
            src = thead-gcc;
          });
        })
      ];
    };
  in
  {
    # cross-build
    nixosConfigurations.lp4a = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      # skip many contents here
      # ......
    };
}
```

测试仍在进行中，目前还不清楚效果如何。




这篇文章主要介绍 NixOS 与 Flakes 的一些实用技巧，以及一些常用的工具。

## other useful tools

- https://github.com/nixpak/nixpak
- https://github.com/maralorn/nix-output-monitor

## NixOS generator

TODO

## 通过 dev-templates 创建开发环境

[numtide/devshell](https://github.com/numtide/devshell) seems to be a personal project, and not documented well.

[cachix/devenv](https://github.com/cachix/devenv) has rich documentation, and the project is very active, so I decided to give it a try.

[dev-templates](https://github.com/the-nix-way/dev-templates) a collection of Nix templates for development environments, may be more intuitive than cachix/devenv for experienced Nix users.

看了一圈三个项目，感觉 dev-templates 最符合我的需求，另外两个项目感觉不到啥优势。

分析下 lib.mkShell 的实现，首先 `nix repl -f '<nixpkgs>'` 然后输入 `:e pkgs.mkShell`:

TODO

## 打包自己的软件

### 1. stdenv 构建介绍

> https://github.com/NixOS/nixpkgs/tree/nixos-unstable/doc/stdenv

TODO

### 2. many language specific frameworks

> https://github.com/NixOS/nixpkgs/tree/nixos-unstable/doc/languages-frameworks

TODO

## 分布式构建

分布式构建可以通过多台机器来分担本地的编译压力，加快构建速度。
常用于 RISC-V 或 ARM64 架构的构建，因为本来 cache.nixos.org 中对 ARM64 的缓存就很少，而 RISC-V 更是几乎没有任何官方缓存，导致需要大量本地编译。
另外嵌入式场景下往往对底层内核、驱动等有定制需求，这也会导致经常需要在本地执行大量编译动作。

- https://github.com/NixOS/nix/blob/713836112/tests/nixos/remote-builds.nix#L46
- https://sgt.hootr.club/molten-matter/nix-distributed-builds/

多机远程构建是以 Derivation 为单位的，在构建的 packages 较多时可以轻松将所有主机的 CPU 都用上，非常爽。

其他发行版也可以用 distcc/ccache 来构建，不过我没试过，不清楚体验如何。

TODO
