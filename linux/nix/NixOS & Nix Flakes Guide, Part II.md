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
