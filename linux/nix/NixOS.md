## NixOS 安装使用

>这是一篇个人学习笔记，目前还比较散乱，待整理。

最近 EndeavourOS 从 i3wm 换成 sway 时把环境搞出问题了，把 sway 干掉也没解决问题，不知道是哪里有变化...

就打算干脆换成可回推的 NixOS 试试。

### 安装

直接从官方文档下载 ISO 镜像安装。

### 名词解释

在真正开始使用 Nix 前，需要先了解下 Nix 的一些名词：

- derivation: 一个构建动作的 nix 语言描述，它描述了如何构建一个软件包，它的执行结果是一个 store object
- store: store object 的存储位置，它是一个只读的文件系统，所有的 store object 都是不可变的。
  - 其位置通常为 `/nix/store`
- sotre object: derivation 的执行结果，它是 store 中的一个文件，它可以是一个普通文件，也可以是一个目录。它可以是一个软件包，也可以是另一个 derivation。
- store path: store object 的路径，它的格式为 `/nix/store/<hash>-<name>`，其中 `<hash>` 是 store object 的 hash，`<name>` 是 store object 的名字。
- substitute: 它是存储在 Nix database 中的一个命令调用，描述了在跳过普通构建过程（如 derivation）的情况下，如何从其他服务器上获取对应的 store object。
  - 这应该就是 nix 的 cache 机制，大部分常用的软件包都可以直接从 cache.nixos.org 上获取，这避免了耗时的本地构建。
- purity: nix 系统假设 derivation 的每次执行总是产生同样的结果，这意味着 derivation 的执行结果只与输入有关，而与执行环境无关。
  - purity 是 nix 系统能通过 substitute 实现缓存、以及它承诺的可复现性的基础。
  - 但是这并不是总能做到，因为 derivation 基本都需要依赖一些外部资源作为输入，如第三方服务器上的资源、时间等，这些东西的变化可能会导致 derivation 的执行结果不同。
- Nix expression： 软件包的一个 nix 语言描述，它被翻译成 derivation 并保存在 store 中。
- user environment: 用户环境，它是一个由 nix 管理的目录，它包含了用户的软件包，以及用户的配置文件。
- Nix Flake: Nix 包管理器的一项重要的新功能，它提供了一种更加简单、可重复、可扩展和灵活的方式来管理软件和系统。
  - 它允许用户将 Nix 包管理器的所有功能打包成一组可重复、可复制和可扩展的“碎片”，称为 Flake。一个 Flake 可以包含 Nix 表达式、NixOS 配置、软件包描述、构建脚本等多个组件，并且通过 flake.lock 文件来锁定其依赖的其他 Flake——以确保 Flake 的可重复性。
  - 目前虽然还是实验性，但是已经实验一年多了（2021-11-11 开始），很多人都在用（感觉就跟 Kubernetes 的 beta API 一样...）。


以及软件仓库相关的名词：

- [nixpkgs](https://github.com/NixOS/nixpkgs) 是一个包含了所有 nix 包与 nixos 模块/配置的 Git 仓库，其 master 分支包含最新的 nix 包与 nixos 模块/配置。
- nixpkgs channel: 共有四个，分别是 stable/unstable，它们实质都对应了 nixpkgss 仓库的不同 commit，stable 每 6 个月更新一次，而 unstable 则直接与 nixpkgs master 分支保持同步，包含了所有已被测试过的最新的 nix 包与 nixos 模块/配置。
  - 此外还有 large 跟 small 两个 channel，large 包含了 nix 包及其二进制缓存，而 small 则只包含了 nix 包。为了避免本地构建，通常使用 large channel。
- NUR: 类似 Arch Linux 的 AUR，NUR 是 Nix 的一个第三方的 nix 包仓库，它包含了一些 nix 包，但是它们并不包含在 nixpkgs 仓库中，因此需要单独安装。

通常我们建议使用 unstable/large 这个 channel，因为它包含了最新的 nix 包与 nixos 模块/配置，而且还包含了 nix 包的二进制缓存，这能避免本地构建，加快安装速度。


### 配置

>https://nixos.wiki/wiki/Overview_of_the_NixOS_Linux_distribution

我的配置目标是：尽量还原我在 EndeavourOS 上的桌面环境，以及安装上所有我常用的软件。


首先考虑下 Nix 有哪些配置项，以及它们的作用：

- 系统配置：`/etc/nixos/configuration.nix`，包括系统的基本配置，如时区、语言、键盘布局、网络、用户、文件系统、启动项等，也包含系统软件的安装与配置。
  - `nixos-rebuild switch` 会根据配置文件生成一个新的系统环境。
  - 上一个系统环境会被保留，而且会被加入到 grub 的启动项中，这确保了你随时可以回退到上一个系统环境。
  - 你甚至可以使用 git 仓库 来保存 `/etc/nixos` 目录，这能确保你的系统环境不会丢失，可以随时还原。
- home manager: 一个管理用户 home 目录下的配置文件的工具。它使用 Nix 表达式来描述用户的配置，并允许用户在多台计算机之间共享他们的配置。使用 home-manager，用户可以安装，配置和更新他们的应用程序，shell，编辑器和其他工具的配置。home-manager 还可以使用 nix-shell 来为每个应用程序创建独立的环境。
  - home manager 在 NixOS 中可作为一个 module 安装使用，并在运行 `nixos-rebuild` 时自动构建用户环境。
  - 能看到 NixOS 自己的配置文件负责管理系统环境，而 home manager 负责管理用户环境。
- Nix Profile: nixos 中的 Profile 类似 Python 的虚拟环境，可以用于创建隔离的软件环境。Profile 存储在 /nix/var/nix/profiles 目录中。默认情况下，系统预定义了一些 Profile，如 system、user 和 nixos-test。
- Nix Container: Nix Container 是一个用于创建隔离的 Nix 环境的工具，它允许用户在一个 Nix 容器中运行一个 NixOS 系统，而不会影响到宿主机的系统环境。可以说它就是 Docker 的 Nix 版本。

可以看到上面的 Nix Profile、Nix Container、Home Manager 都可以用来创建隔离的软件环境，不过 Home Manager 还可以管理 Home 目录下的其他东西，因此好像 Home Manager 用得多一点。

有几个命令需要介绍下：

- nix-env：nix-env 是 Nix 包管理器的一部分，它允许用户在其系统上全局安装 Nix 包。使用 nix-env，用户可以安装，更新和卸载 Nix 包，并将它们添加到他们的 $PATH 中。
  - 但是要注意的是，只有通过 `/etc/nixos/configuration.nix` 等声明式配置安装的软件才能被 nixos-rebuild 管理，而通过 nix-env 安装的软件完全来自 nix channel，也没有什么版本锁定的概念，所以可能会导致系统环境的不一致，也无法复现，与其他系统比不存在任何优势。
  - 总的来说，nix-env 就跟其他操作系统的包管理器差不多，为了系统的可复现性，应该尽量避免使用 nix-env 来安装软件。
- nix-shell：nix-shell 允许用户在临时环境中运行命令，这个环境包含所有必需的依赖项和环境变量。这使得用户能够为一个特定的项目创建一个独立的环境，并确保所有依赖项都满足项目的要求。nix-shell 还可以从一个 Nix 表达式（例如一个 default.nix 文件）中生成一个环境。
- direnv: direnv 是一个 shell 扩展，它能够根据当前目录的环境变量来修改 shell 的行为。它可以用来管理项目的依赖，比如使用 nix-shell 来管理项目的依赖，或者使用 nix-env 来管理项目的依赖。


## 正式使用

>这里假设你已经了解 Nix 语言的基本语法。

### 1. 启用 openssh 服务

然后添加 openssh 相关配置，参数可以在 <https://search.nixos.org/options> 中查到：

```nix
{ config, pkgs, ... }:

{

  # Define a user account. Don't forget to set a password with ‘passwd’.
  users.users.ryan = {
    isNormalUser = true;
    description = "ryan";
    extraGroups = [ "networkmanager" "wheel" ];
    openssh.authorizedKeys.keys = [
        # replace with your own public key
        "ssh-ed25519 some-public-key ryan@ryan-pc"
    ];
    packages = with pkgs; [
      firefox
    #  thunderbird
    ];
  };

  # Enable the OpenSSH daemon.
  services.openssh = {
    enable = true;
    permitRootLogin = "no";         # disable root login
    passwordAuthentication = false; # disable password login
    openFirewall = true;
    forwardX11 = true;              # enable X11 forwarding
  };
}
```

这里我启用了 openssh 服务，并为 ryan 用户添加了 ssh 公钥，这样我就可以通过 ssh 登录到我的系统了。

然后运行 `nixos-rebuild switch` 后，就能使用我的私钥登录系统了，密码登录会直接报错。

### 2. 启用 nix flake

前面提到了 flake 提供了 flake.lock 确保系统可复现，而我的目标正是打造一个可复现的系统，所以我决定使用 flake 来管理我的系统。

但是目前 flake 作为一个实验性的功能，仍未被默认启用。所以我们需要手动启用它，修改 `/etc/nixos/configuration.nix` 文件，在函数块中启用 flakes 与 nix-command 功能：

```nix
{ config, pkgs, ... }:

{
  nix.settings.experimental-features = [ "nix-command" "flakes" ];
}
```

然后运行 `nixos-rebuild switch` 应用修改。


#### 2.1 学习 flake 的编写方式

可以首先使用官方提供的模板来学习 flake 的编写，先查下有哪些模板：

```bash
nix flake show templates
```

其中有个 `templates#full` 模板展示了所有可能的用法，可以看看它的内容：

```bash
nix flake init -t templates#full
cat flake.nix
```

简单浏览后，我们创建文件 `/etc/nixos/flake.nix`，后续系统的所有修改都将全部由 nix flake 接管，参照前面的模板，编写如下内容：

```nix
{
  description = "Ryan's NixOS Flake";

  # 输入配置，即软件源
  inputs = {
    # NixOS 官方软件源
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    # home-manager，用于管理用户配置
    home-manager = {
      url = "github:nix-community/home-manager/release-22.11";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  # 输出配置，即 NixOS 系统配置
  outputs = { self, nixpkgs, ... }@inputs: {
    # 定义一个名为 nixos 的系统
    nixosConfigurations."nixos" = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      # 导入之前我们使用的 configuration.nix，这样旧的配置文件仍然能生效
      modules = [
        ./configuration.nix
      ];
    };
  };
}
```

这里我们定义了一个名为 nixos 的系统，它的配置文件为 `./configuration.nix`，这个文件就是我们之前的配置文件，这样我们仍然可以沿用旧的配置。

现在执行 `nixos-rebuild switch` 应用配置。


### 3 安装 home-manager

根据官方文档 [Home Manager Manual](https://nix-community.github.io/home-manager/index.htm)，安装流程如下：

首先，我希望将 home manager 作为 NixOS 模块安装，首先需要创建 `/etc/nixos/home.nix`，官方给出了样板：

```nix
{ config, pkgs, ... }:

{
  # Home Manager needs a bit of information about you and the
  # paths it should manage.
  # 注意修改这里的用户名与用户目录
  home.username = "ryan";
  home.homeDirectory = "/home/ryan";

  # Packages that should be installed to the user profile.
  home.packages = [ 
    # 用户目录下安装的软件包                              
    pkgs.htop
  ];

  # git 相关配置
  programs.git = {
    enable = true;
    userName = "Ryan Yin";
    userEmail = "xiaoyin_c@qq.com";
  };

  programs.starship = {
    enable = true;
    settings = {
      add_newline = false;
      aws.disabled = true;
      gcloud.disabled = true;
      line_break.disabled = true;
    };
  };

  # alacritty 终端配置，貌似还需要配置 X11 环境，否则无法启动
  programs.alacritty = {
    enable = true;
    settings = {
      colors = {
        primary = {
          background = "0x282828";
          foreground = "0xebdbb2";
        };
        normal = {
          black = "0x282828";
          red = "0xcc241d";
          green = "0x98971a";
          yellow = "0xd79921";
          blue = "0x458588";
          magenta = "0xb16286";
          cyan = "0x689d6a";
          white = "0xa89984";
        };
        bright = {
          black = "0x928374";
          red = "0xfb4934";
          green = "0xb8bb26";
          yellow = "0xfabd2f";
          blue = "0x83a598";
          magenta = "0xd3869b";
          cyan = "0x8ec07c";
          white = "0xebdbb2";
        };
      };
      env.TERM = "xterm-256color";
      font = {
        size = 12;
        draw_bold_text_with_bright_colors = true;
      };
      hints = {
        alphabet = "jfkdls;ahgurieowpq";
        enabled = [{
          regex = "(https:|http:|git:|ftp:)[^\\u0000-\\u001F\\u007F-\\u009F<>\"\\\\s{-}\\\\^⟨⟩`]+";
          command = "${pkgs.xdg-utils}/bin/xdg-open";
          post_processing = true;
          mouse = { enabled = true; mods = "Alt"; };
        }];
      };
      scrolling.multiplier = 5;
      selection.save_to_clipboard = true;
    };
  };

  # This value determines the Home Manager release that your
  # configuration is compatible with. This helps avoid breakage
  # when a new Home Manager release introduces backwards
  # incompatible changes.
  #
  # You can update Home Manager without changing this value. See
  # the Home Manager release notes for a list of state version
  # changes in each release.
  home.stateVersion = "22.11";

  # Let Home Manager install and manage itself.
  programs.home-manager.enable = true;
}
```

然后再使用如下命令在 `/etc/nixos` 中创建 home-manager 的 flake.nix 配置：

```shell
nix flake new /etc/nixos -t github:nix-community/home-manager#nixos
```

通过模板生成好 `/etc/nixos/flake.nix` 配置后不是万事大吉，还得手动改下相关参数：

```nix
{
  description = "NixOS configuration";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    home-manager.url = "github:nix-community/home-manager";
    home-manager.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = inputs@{ nixpkgs, home-manager, ... }: {
    nixosConfigurations = {
      # 这里替换成你的主机名称
      <your-hostname> = nixpkgs.lib.nixosSystem {
        system = "x86_64-linux";
        modules = [
          ./configuration.nix
          home-manager.nixosModules.home-manager
          {
            home-manager.useGlobalPkgs = true;
            home-manager.useUserPackages = true;
            # 这里的 ryan 也得替换成你的用户名
            home-manager.users.ryan = import ./home.nix;

            # Optionally, use home-manager.extraSpecialArgs to pass
            # arguments to home.nix
          }
        ];
      };
    };
  };

}
```

然后执行 `nixos-rebuild switch` 应用配置。

### 4. 配置 i3wm 窗口管理器

首先，确保在 `/etc/nixos/configuration.nix` 中添加如下配置：

```nix
{ config, pkgs, ... }:

{
  services.xserver.enable = true;
}
```

然后既然我们已经安装了 home manager，i3wm 可以直接在 `/etc/nixos/home.nix` 中配置，添加如下内容：

```nix
{ config, pkgs, ... }:

{
  # Enable the i3 windows manager
  xsession = {
    enable = true;
    windowManager.i3 = {
      enable = true;
      config = {
        bars = {
          status = {
            position = "bottom";
            statusCommand = "i3status-rust";
          };
        };
      };
    };
  };

}
```

## 参考

- [NixOS 系列（一）：我为什么心动了](https://lantian.pub/article/modify-website/nixos-why.lantian/): 这是 LanTian 大佬的 NixOS 系列文章，写得非常清晰明了，新手必读。
- [Nix Flakes Series](https://www.tweag.io/blog/2020-05-25-flakes/): 官方的 Nix Flake 系列文章，介绍得比较详细，作为新手入门比较 OK
- [Nix Flakes - Wiki](https://nixos.wiki/wiki/Flakes): Nix Flakes 的官方 Wiki，此文介绍得比较粗略。
- 一些参考 nix 配置
  - [xddxdd/nixos-config](https://github.com/xddxdd/nixos-config)
  - [bobbbay/dotfiles](https://github.com/bobbbay/dotfiles)
  - [gytis-ivaskevicius/nixfiles](https://github.com/gytis-ivaskevicius/nixfiles)
  - [fufexan/dotfiles](https://github.com/fufexan/dotfiles): 好漂亮，教练我想学这个
  - [davidak/nixos-config](https://codeberg.org/davidak/nixos-config)
  - [davidtwco/veritas](https://github.com/davidtwco/veritas)
- [NixOS 手册](https://nixos.org/manual/nixos/stable/index.html): 要想把 NixOS 玩透，这是必读的。前面的文章读来会发现很多陌生的概念，需要靠这个补全。
  - 不过也不是说要把所有内容都补一遍，先看个大概，后面有需要再按图索骥即可。



