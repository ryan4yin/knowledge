# [Ansible](https://github.com/ansible/ansible)

## 前言：Fabric 介绍

我日常的自动化 CI/CD 代码里，经常杂含了各种数据处理(json/yaml)、HTTP API 调用、本地命令调用(go/dotnet/flutter)、远程命令调用(ssh 远程命令)、数据传输(ftp/ssh/http)等等。
其中数据处理用 json/pyyaml，本地命令调用有 `subprocess`。
而远程命令调用有 `paramiko` 和 `fabric`。`paramiko` 比较底层，用着不方便；

`fabric` 比较符合我的需求，于是我自己基于 `fabric.Connection` 封装了一个 SSH 帮助类（加了些自己需要的功能），用于远程执行命令、传输数据。
另外，可以使用 `fabric.SerialGroup('host1', 'host2', 'host3')` 在多台主机上执行同样的操作，
或者通过 `fab -H web1,web2,web3 xxx` 命令和 `fabric.task` 装饰器进行批量操作，这样做的好处是主机可以临时在命令行指定。

我主要还是将 `fabric` 当成一个 ssh client 用，它比较适合用来在 python 代码中处理一些简单的远程命令、数据传输。

但对于更复杂的 devops 任务，用 `fabric` 可能就有些难度了。为此现在开始学习 Ansible.

## Ansible 说明

Ansible 和 Fabric 一样，都是基于 pramiko(ansible 也能用 openssh，性能更好)，使用 ssh 协议连接到远程主机上运行命令，但是两个项目的规模却不是一个量级的。

对标容器编排领域，Ansible 就好比 Kubernetes，从具体场景中提炼出了一些抽象概念，需要花时间去学习它的这一套抽象概念。
而 Fabric 就类似 Docker Swarm Mode，走的是极简的路子，用起来很方便，但是不适合更复杂的场景。

另外 Ansible 和 Kubernetes 还有一个共同点，就是它们灵活的「插件」机制，Ansible 社区提供了数千个实用的 Modules 来完成一些通用的任务（而且还在不断增多），Kubernetes 生态圈也是百花齐放——[CNCF LandScape](https://landscape.cncf.io/)。

## 安装 ansible

```shell
# 我比较习惯使用 pip 安装
pip install --user ansible paramiko
# 如果你需要使用密码登录（你的网络环境比较安全），还需要安装 sshpass
sudo apt-get install sshpass
```

## 参考

- [ansible docs](https://docs.ansible.com/)
