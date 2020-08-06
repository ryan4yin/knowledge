# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Union, Optional, IO

import paramiko
from fabric import Connection
from invoke import UnexpectedExit

from .common import random_string
from .file import tar_files

"""
通过 ssh 协议与远程主机交互：
    1. 使用 Connection.run() 远程执行命令（或者 Connection.sudo()，执行 root 命令）
    2. 使用 Connection.put()/Connection.get()，通过 sftp 协议传输文件

更复杂的操作建议使用 ansible
"""


class SSH(object):
    """
    对 Fabric 的一个简单的封装：
        1. 屏蔽了一些暂时用不到的参数。
        2. 设置了一些对 debug 有利的默认参数
        3. 添加了额外的中文 docstring
    """

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: Optional[str] = None,
        key_file_obj: IO = None,
        key_file_path: Optional[Path] = None,
        key_file_passphrase: Optional[str] = None,
    ):
        """
        使用示例：
        ```python3
        # 1. 使用密码登录远程主机
        ssh_con = SSH("<host>", 22, username="<username>", password="<password>")

        # 2. 使用私钥登录远程主机（私钥没有设置 passphrase）
        ## 2.1 指定密钥位置
        ssh_con = SSH("<host>", 22, username="<username>", key_file_path=Path("~/.ssh/id_rsa"))
        ## 2.2 给出密钥的 IO 对象
        ssh_con = SSH("<host>", 22, username="<username>", key_file_obj=Path("~/.ssh/id_rsa").open(encoding='utf-8'))
        ```
        """
        connect_kwargs = dict()
        if key_file_obj is not None:
            private_key = paramiko.RSAKey.from_private_key(
                key_file_obj,
                key_file_passphrase
            )
            connect_kwargs['pkey'] = private_key
        elif key_file_path is not None:
            connect_kwargs = {
                "key_filename": str(key_file_path.resolve()),
                "passphrase": key_file_passphrase
            }
        elif password is not None:
            connect_kwargs['password'] = password
        else:
            raise KeyError("must given password/pkey/private_key")

        self.conn = Connection(
            host=host,
            port=port,
            user=username,
            connect_kwargs=connect_kwargs
        )

    def open(self):
        """建立连接。
        使用 run/put/get 命令时，会自动创建连接。
        但是 cd 不行，因为 cd 只是修改本地 session 的东西
        """
        return self.conn.open()

    def close(self):
        """关闭连接"""
        return self.conn.close()

    @property
    def is_connected(self):
        return self.conn.is_connected

    def run(self, cmd: str,
            warn=False,
            hide=False,
            echo=True,
            **kwargs):
        """
        远程执行命令

        使用示例：
        ```python3
        # 1. 执行命令，打印出被执行的命令，以及命令的输出。命令失败抛出异常
        ssh_con.run("ls -al")
        # 2. 执行命令，命令失败只抛出 warn（对程序的运行没有影响），这样可以手动处理异常情况。
        result = ssh_con.run("ls -al", warn=True)
        if result.return_code != 0:  # 命名执行失败
            # 处理失败的情况

        # 3. 拉取 docker 镜像，只在命令失败的情况下，才输出 docker 命令的日志。
        result = ssh_con.run("docker pull xxxx", hide=True, warn=True)
        if result.return_code != 0:  # 运行失败
            logger.error(result.stdout)  # 打印出错误日志，这里 stdout 一般会包含 stderr
            # 然后考虑要不要抛出异常
        ```

        ==================
        注意！！！run/sudo 并不记录 cd 命令切换的路径！
        如果需要改变 self.cwd （当前工作目录），必须使用 self.cd() 函数，详细的用法参见该函数的 docstring

        官方文档：http://docs.pyinvoke.org/en/0.12.1/api/runners.html#invoke.runners.Runner.run
        :param cmd: 命令字符串
        :param warn: 命令非正常结束时，默认抛异常。如果这个为 True，就只发出 Warning，不抛异常
        :param hide: 是否隐藏掉命令的输出流（stdout/stderr）
        :param echo:是否回显正在运行的命令（最好选择回显，debug很有用）
        :param shell: 指定用于执行命令的 shell
        :param encoding: 字符集
        :return: 一个 Result 对象，该对象的主要参数有：
            command: 被执行的命令
            ok: A boolean equivalent to exited == 0.
            return_code: 命令返回值
            stdout: 命令的标准输出，是一个多行字符串
                程执行命令时可能无法区分 stdout/stderr，这时 stdout 会包含 stderr
        """
        return self.conn.run(
            command=cmd,
            warn=warn,
            hide=hide,
            echo=echo,
            **kwargs
        )

    def sudo(self, command, **kwargs):
        """以 sudo 权限执行命令
        如果设置了密码，就自动使用该密码。
        否则会要求在命令行输入密码（这对运维来说显然不可取）

        注意！！！run/sudo 并不记录 cd 命令切换的路径！
        如果需要改变 self.cwd （当前工作目录），必须使用 self.cd() 函数，详细的用法参见该函数的 docstring

        """
        return self.conn.sudo(command=command, **kwargs)

    def local(self, *args, **kwargs):
        """在本机执行命令"""
        return self.conn.local(*args, **kwargs)

    def cd(self, path: Union[Path, str]):
        """change dir
        self.run()/self.sudo() 命令不会记录由 `cd` 命令造成的工作目录改变，
        要使多个语句都在某个指定的路径下执行，就必须使用 self.cd()，
        （或者你手动在每个 run 指令前，加上 cd /home/xxx/xxx，显然不推荐这么干）

        重点！这是一个类似 open(xxx) 的函数，需要使用 with 做上下文管理。
        用法：
        ```
        with ssh_conn.cd("/tmp"):
            # do some thing
        ```
        出了这个 with 语句块，cd 就失效了。

        ---
        实际上就是给 with 语句块中的每个 run/sudo 命令，添加上 `cd xxx`
        """
        return self.conn.cd(str(path))

    @property
    def cwd(self):
        """currently work dir
        默认为空字符串，表示 $HOME
        """
        return self.conn.cwd

    def get(self, remote_file_path: Union[Path, str],
            local: Union[Path, IO] = None,
            preserve_mode: bool = True,
            mkdirs=False):
        """
        从远程主机获取文件到本地
        :param remote_file_path: 远程主机上的文件的路径（不会解析 `~` 符号！建议用绝对路径！）
        :param local: 将文件保存到本地的这个位置/flie-like obj。若未指定，会存放在当前工作目录下(os.getcwd())
        :param preserve_mode: 是否保存文件的 mode 信息（可读/可写/可执行），默认 True
        :param mkdirs: 如果路径不存在，是否自动创建中间文件夹。
        :return: 一个 Result 对象
        """
        if isinstance(local, Path):
            local_path_parent = local.parent
            if local_path_parent.exists() is False:
                if mkdirs:
                    local_path_parent.mkdir(parents=True)
                else:
                    raise FileNotFoundError(
                        "directory '{}' not exist!".format(local_path_parent))

        return self.conn.get(
            remote=str(remote_file_path),
            local=local,
            preserve_mode=preserve_mode,
        )

    def put(self, local: Union[Path, IO],
            remote_file_path: Union[Path, str] = Path("."),
            preserve_mode: bool = True,
            mkdirs=False):
        """
        将文件从本地传输给远程主机

        :param local: 本机的文件路径/ file-like obj
        :param remote_file_path: 将文件保存到远程主机上的这个路径下（不会解析 `~` 符号！建议用绝对路径！）
                                 默认传输到远程的 home 目录下
        :param preserve_mode: 是否保存文件的 mode 信息（可读/可写/可执行），默认 True
        :param mkdirs: 如果路径不存在，是否自动创建中间文件夹。
        :return: 一个 Result 对象，该对象不包含 ok 等属性。。。
        """
        if mkdirs:
            parent = Path(remote_file_path).parent
            self.conn.run("mkdir -p '{}'".format(parent))

        return self.conn.put(
            local=local,
            remote=str(remote_file_path),
            preserve_mode=preserve_mode
        )

    def put_dir(self, local_dir_path: Union[Path, IO],
                remote_path: Union[Path, str] = Path("."),
                preserve_mode: bool = True,
                mkdirs=False):
        """
        将文件夹从本地传输给远程主机

        :param local_dir_path: 本机的文件夹路径
        :param remote_path: 远程主机中的文件夹路径（不会解析 `~` 符号！建议用绝对路径！）
                            默认传输到远程的 home 目录下
                            如果此文件夹路径不存在，会提前创建它
        :param preserve_mode: 是否保存文件的 mode 信息（可读/可写/可执行），默认 True
        :param mkdirs: 如果路径不存在，是否自动创建中间文件夹。
        :return
        """
        try:
            self.conn.run(f"test -d {Path(remote_path).as_posix()}")
        except UnexpectedExit:
            self.conn.run(f"mkdir -p {Path(remote_path).as_posix()}")

        stream = tar_files(local_dir_path, c_type="gz", get_stream=True)
        tar_name = local_dir_path.name + ".tar.gz"
        stream.name = tar_name
        self.put(local=stream,
                 remote_file_path=str(remote_path),
                 preserve_mode=preserve_mode,
                 mkdirs=mkdirs)
        with self.cd(remote_path):
            self.run("tar -ax -f {}".format(tar_name))
            self.run("rm {}".format(tar_name))
