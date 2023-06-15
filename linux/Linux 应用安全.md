# Linux 应用安全

> https://wiki.archlinux.org/title/Security

Linux 安全是一个很大的话题，上面给出的 Arch Linux Wiki 涵盖了其中几乎所有的部分，不过这里只讨论其中一部分我关注的内容。

## MAC 强制访问控制

Linux 内核提供了 LSM（Linux Kernel Security Modules）框架，它为其他内核模块提供了一系列实现内核安全模块缩必须的 Hooks。
Linux 社区有许多基于 LSM 的安全模块，如 SELinux、AppArmor、Smack、TOMOYO、Yama 等，其中 SELinux 和 AppArmor 是最为流行的两个。

首先简单介绍下这俩：

1. SELinux
   1. 我很久前使用 CentOS 时就听说过 SELinux，记得它好像是给我使用 Docker 造成了些麻烦，网上各种资料都说它很难配置，建议直接关闭，所以我也就没有深入了解过，每次都是直接关掉了。
2. AppArmor
   1. 一个比 SELinux 更加简单的 LSM，顾名思义，它是基于应用的安全模块，可以为每个应用指定安全策略，限制应用的权限，防止应用越权访问系统资源。

先介绍几个关键词：

1. DAC(Discretionary Access Control) 自主访问控制
   1. DAC 是 Linux 默认的访问控制机制，它是基于用户的访问控制，用户可以自由的控制自己的对象，如文件、进程等。我们常用的 chmod/chown 都是 DAC 的典型代表。
   2. 它的缺点是粒度太粗，只能控制用户对对象的权限，该用户启动的所有子进程都会继承用户的权限，不能对每个子进程单独设置权限——这风险太大了。
2. MAC(Manadatory Access Control) 强制访问控制
   1. MAC 强制访问控制中，安全策略由安全策略管理员集中控制，用户无权覆盖策略。
      1. 相比而言，自主访问控制（DAC）也控制主体访问对象的能力，但允许用户进行策略决策和/或分配安全属性。

那么这里讨论的 LSM 就都是 MAC 在 Linux 上的一种实现，它与 Linux 中现有的 DAC 机制（rwx）共同工作（但优先级高于 DAC），提供了更加细粒度的访问控制。

此外 Linux 中超级用户 root 可以绕过 DAC 机制，访问系统中的任何对象，但是它不能绕过 MAC 机制，所以 MAC 机制也可以用来限制 root 用户。如果你发现你的 root 用户失去了对某些对象的访问权限，那么很有可能是 MAC 机制在起作用。

### 1. AppArmor

> https://wiki.archlinux.org/title/AppArmor

AppArmor 是 MAC 机制的一种实现，它与 Linux 中已有的 DAC 机制共同工作，提供了更加细粒度的访问控制。

Ubuntu, SUSE, NixOS 和 Manjaro 等发行版默认都使用 AppArmor，而 RHEL 及其衍生发行版则默认使用 SELinux。

SELinux 虽然功能强大，但配置复杂，需要好的用户空间集成，而且还要求使用受支持的文件系统，而 AppArmor 则更加简单，它基于文件路径来工作，配置更加容易。

AppArmor 通过在每个应用程序的级别强制执行一系列的安全策略，避免操作系统与应用程序受内部威胁甚至 0-day 漏洞攻击。
这一系列安全策略完全定义了每个应用程序可以访问的系统资源以及所拥有的特权。如果没有策略说可以，那么默认情况下是拒绝访问的（deny by default）。
AppArmor 附带了一些默认策略，使用静态分析和基于学习的工具的组合，即使是非常复杂的应用程序，也可以在几个小时内成功部署 AppArmor 策略。

每次违反策略都会被 AppArmor 拦截，同时在系统日志中触发一条消息，AppArmor 可以配置为在桌面上弹出实时违规警告，通知用户。

#### NixOS 中的 AppArmor

> https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/security/apparmor.nix

TODO

### 2. SELinux

> https://wiki.archlinux.org/title/SELinux

SELinux 主要被 Red Hat 及其衍生发行版支持，NixOS/Ubuntu 等发行版默认使用 AppArmor，其中 NixOS 明确表示不支持 SELinux。
不过 Arch Linux 倒是两个都支持。

## SecComp

> https://man7.org/linux/man-pages/man2/seccomp.2.html

Seccomp 代表安全计算（Secure Computing）模式，自 2.6.12 版本以来，一直是 Linux 内核的一个特性。 它可以用来沙箱化进程的权限，限制进程从用户态到内核态的调用。 Kubernetes 能使你自动将加载到节点上的 seccomp 配置文件应用到你的 Pod 和容器。

后面要介绍的 firejail/bubblewrap/Flatpak/Docker 底层都使用了 SecComp.

### Kubernetes 中的 SecComp

> https://kubernetes.io/zh-cn/docs/tutorials/security/seccomp/

TODO

Kubernetes 也提供了对 AppArmor 的支持，但是从 Kubernetes 1.4 开始进入 beta 后，到现在 1.27 都没半点动静，说明有这需求的人估计不多...

更详细的信息可以看看社区的这个 operator: https://github.com/kubernetes-sigs/security-profiles-operator

## 沙盒程序

沙盒有很多种：

1. 最安全也最重量级的肯定是虚拟机了，但是虚拟机太重了，而且也不是每个程序都需要这么高的安全性。
2. 比虚拟机轻量些的，是容器技术，比如 Docker/Podman，但是容器技术一是不太适合 GUI 应用，而且文件系统的完全隔离有点太重了。
3. 再轻量一级的就是 firejail 与 bubblewrap 了，它们与容器一样都是基于 Linux 的命名空间机制实现的，但是它们的隔离程度比容器要低，也就更加轻量，很适合桌面应用。

所以总的来说，对于桌面应用，建议使用 firejail 或者 bubblewrap，对于服务器应用，建议使用容器技术。

### 1. firejail

[Firejail](https://wiki.archlinuxcn.org/wiki/Firejail) 是一个易于使用的、简单的工具，用于沙盒化程序和服务器。建议将 Firejail 也用于浏览器以及其他网络应用程序，就像对待正在运行的服务器程序一样。

### 2. bubblewrap

[bubblewrap](https://github.com/containers/bubblewrap) 是一个由 Flatpak 开发的基于 setuid 的沙盒程序，其资源占用比 Firejail 更小。虽然它缺少某些功能，例如文件路径白名单，但 bubblewrap 确实提供了 bind mounts 的功能，能够创建 user/IPC/PID/network/cgroup 命名空间，并且可以支持简单和 复杂的沙盒。

### 3. 容器技术

最著名的就是 Docker/Podman 了。

### 4. 其他虚拟化技术

如 QEMU/KVM、VirtualBox 等

## Linux PAM

> https://wiki.archlinuxcn.org/wiki/PAM

Linux PAM (Pluggable Authentication Modules) 是一个系统级用户认证框架。

PAM 将程序开发与认证方式进行分离，程序在运行时调用附加的“认证”模块完成自己的工作。本地系统管理员通过配置选择要使用哪些认证模块。

Linux 世界中有许多 Linux PAM 认证模块，常见的有：

1. 密码认证模块：pam_unix.so
2. 两步认证模块：pam_google_authenticator.so
3. 通过远端 LDAP 服务器认证：pam_ldap.so
4. 指纹认证模块：pam_fprintd.so
5. 通过 USB 加密狗认证：pam_usb.so

此外还有一些安全限制模块，如：

1. 强制密码认证：pam_cracklib.so

PAM 可插拔认证模块在 macOS 中也同样存在，可以通过简单的配置文件修改，使 macOS 支持通过指纹来进行 sudo 指令认证，免去输入密码的麻烦。

## 参考

- [Introduction To Firejail, AppArmor, and SELinux - Youtube](https://www.youtube.com/watch?v=JFjXvIwAeVI)
  - and a post of it [Introduction To Firejail, AppArmor, and SELinux](https://retro64xyz.gitlab.io/presentations/2018/10/16/firejail-and-apparmor/)
