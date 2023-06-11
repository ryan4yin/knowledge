## Nix Modules System

- [Nix modules: Improving Nix's discoverability and usability ](https://cfp.nixcon.org/nixcon2020/talk/K89WJY/)

建议一读模块系统的完整实现：

https://github.com/NixOS/nixpkgs/blob/nixos-23.05/lib/modules.nix

### nix repl

首先第一步，是使用 `:?` 查看帮助：

```
› nix repl -f '<nixpkgs>'
Welcome to Nix 2.13.3. Type :? for help.

Loading installable ''...
Added 17755 variables.
nix-repl> :?
The following commands are available:

  <expr>        Evaluate and print expression
  <x> = <expr>  Bind expression to variable
  :a <expr>     Add attributes from resulting set to scope
  :b <expr>     Build a derivation
  :bl <expr>    Build a derivation, creating GC roots in the working directory
  :e <expr>     Open package or function in $EDITOR
  :i <expr>     Build derivation, then install result into current profile
  :l <path>     Load Nix expression and add it to scope
  :lf <ref>     Load Nix flake and add it to scope
  :p <expr>     Evaluate and print expression recursively
  :q            Exit nix-repl
  :r            Reload all files
  :sh <expr>    Build dependencies of derivation, then start nix-shell
  :t <expr>     Describe result of evaluation
  :u <expr>     Build derivation, then start nix-shell
  :doc <expr>   Show documentation of a builtin function
  :log <expr>   Show logs for a derivation
  :te [bool]    Enable, disable or toggle showing traces for errors
```

### 模块系统的特殊参数

```nix

_module.args: https://github.com/NixOS/nixpkgs/blob/nixos-23.05/lib/modules.nix#L123

```

通过 `nix repl -f <nixpkgs>` 来查看 `nixpkgs` 中的所有函数和变量的实现逻辑：

```shell
› nix repl -f '<nixpkgs>'
Welcome to Nix 2.13.3. Type :? for help.

Loading installable ''...
Added 17755 variables.
nix-repl> lib.mkDefault
«lambda @ /nix/var/nix/profiles/per-user/root/channels/nixos/lib/modules.nix:899:26»
```

上面打印出了 `lib.mkDefault` 的实现逻辑，可以看到它是一个 lambda 函数，它的实现逻辑在 `/nix/var/nix/profiles/per-user/root/channels/nixos/lib/modules.nix` 文件中的第 899 行的第 26 列。

查看该位置前后 50 行代码 `cat /nix/var/nix/profiles/per-user/root/channels/nixos/lib/modules.nix | tail -n +880 | head -n 50`：

> 当然这个 lib 的代码，你也能在 nixpkgs 仓库中差不多的地方找到，比如： https://github.com/NixOS/nixpkgs/blob/nixos-23.05/lib/modules.nix#L913

```nix
  /* Properties. */

  mkIf = condition: content:
    { _type = "if";
      inherit condition content;
    };

  mkAssert = assertion: message: content:
    mkIf
      (if assertion then true else throw "\nFailed assertion: ${message}")
      content;

  mkMerge = contents:
    { _type = "merge";
      inherit contents;
    };

  mkOverride = priority: content:
    { _type = "override";
      inherit priority content;
    };

  mkOptionDefault = mkOverride 1500; # priority of option defaults
  mkDefault = mkOverride 1000; # used in config sections of non-user modules to set a default
  mkImageMediaOverride = mkOverride 60; # image media profiles can be derived by inclusion into host config, hence needing to override host config, but do allow user to mkForce
  mkForce = mkOverride 50;
  mkVMOverride = mkOverride 10; # used by ‘nixos-rebuild build-vm’

  mkFixStrictness = lib.warn "lib.mkFixStrictness has no effect and will be removed. It returns its argument unmodified, so you can just remove any calls." id;

  mkOrder = priority: content:
    { _type = "order";
      inherit priority content;
    };

  mkBefore = mkOrder 500;
  mkAfter = mkOrder 1500;

  # The default priority for things that don't have a priority specified.
  defaultPriority = 100;

  # Convenient property used to transfer all definitions and their
  # properties from one option to another. This property is useful for
  # renaming options, and also for including properties from another module
  # system, including sub-modules.
  #
  #   { config, options, ... }:
  #
```

能看到 `lib.mkDefault` 函数的实现逻辑是 `mkOverride 1000`，那我们在使用 `lib.mkDefault xxx` 时，实际上是调用了 `mkOverride 1000 xxx`，返回的是一个 attribute set，结构大致如下：

```nix
{
    _type = "override";
    priority = 1000;
    content = xxx;
}
```

其中 `_type` 是 Nix 模块系统的特殊属性，用来标识该 attribute set 的类型，在 Nix 中所有大部分复杂对象都是以 attribute set 的形式存在的，并且通过 `_type` 来标明该对象的类型。

而这个 override 对象，官方文档没有任何解释，还是继续直接看源码实现。

总之根据上面描述，`mkForce` 优先级为 50，是优先级最高的，而 `mkDefault` 优先级为 1000，是优先级最低的，所以使用 `mkForce` 设置的值大概会覆盖 `mkDefault`。

可以在该代码中进一步定位到使用 `_type` 的值进行处理的逻辑： https://github.com/NixOS/nixpkgs/blob/nixos-23.05/lib/modules.nix#L346

那么总结下，mkOptionDefault/mkDefault/mkForce 等几个函数，都是用于定义不同优先级的属性值的。
当多个 Module 都定义了同一个属性的值并且值不同时，优先级高的会覆盖优先级低，优先级相同的会报错。

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

同理现在看看 linuxManualConfig 的定义：发现它居然是 ``

## devenv

[numtide/devshell](https://github.com/numtide/devshell) seems to be a personal project, and not documented well.

[cachix/devenv](https://github.com/cachix/devenv) has rich documentation, and the project is very active, so I decided to give it a try.

[dev-templates](https://github.com/the-nix-way/dev-templates) a collection of Nix templates for development environments, may be more intuitive than cachix/devenv for experienced Nix users.

## other useful tools

- https://github.com/nixpak/nixpak
- https://github.com/maralorn/nix-output-monitor

## disk encryption

Physicial disk may borked, and you need to repair it by send it back to the manufacturer. In this case, you may have some sensitive data on it and you would suffer from data leakage, because the manufacturer may not be trusted, and they can read data directly from the disk.

so the best way to protect your data is to encrypt the disk all the time, you can encrypt the disk with a password to protect your data.

https://gist.github.com/ladinu/bfebdd90a5afd45dec811296016b2a3f

https://www.reddit.com/r/NixOS/comments/xrgszw/nixos_full_disk_encryption_with_tpm_and_secure/

https://github.com/NixOS/nixpkgs/blob/nixos-23.05/nixos/doc/manual/configuration/luks-file-systems.section.md
