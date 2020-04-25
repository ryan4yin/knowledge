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



