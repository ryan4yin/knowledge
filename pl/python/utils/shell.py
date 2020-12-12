# -*- coding: utf-8 -*-


import os
import shutil
import shlex
import subprocess
from pathlib import Path
from contextlib import contextmanager

from typing import Union

import logging
logger = logging.getLogger(__name__)


"""
通过 subprocess 调用其他命令行程序
"""


def run_cmd(cmd: str,
            shell: bool = False,
            input=None,
            timeout: float = None,
            check: bool = False,
            show_logs: bool = True,
            cwd: Path = None, **kwargs):
    """运行指定的命令
        只能同步运行（就是说这个函数是阻塞的），要异步运行指定命令，请手动调用 subprocess.Popen
    =============
    使用示例：
    ```python3
    1. 拉取 docker 镜像，如果失败，抛出异常。
    run_cmd("docker pull xxxx", check=True)

    2. 拉取 docker 镜像，然后手动检查 returncode
    result = run_cmd("docker pull xxxx")
    if result.returncode != 0:  # 命令失败
        # 处理失败情况

    3. 拉取 docker 镜像，只在命令失败的情况下，才输出 docker 命令的日志。
    result = run_cmd("docker pull xxxx", capture_output=True)
    if result.returncode != 0:  # 运行失败
        logger.error(result.stderr)  # 打印出错误日志
        # 然后考虑要不要抛出异常
    ```
    =============
    :param cmd: 命令字符串
    :param shell: 是否使用 shell 运行命令，可以直接运行 shell 脚本！
    :param input: 标准输出
    :param timeout: 命令超时时间
    :param check: 如果命令失败，是否抛出异常？
    :param show_logs: 是否输出详细日志
    :param capture_output: 是否捕获子程序输出的所有日志？
    :param cwd: 命令运行前，将工作路径切换到 cwd 指定的位置
    :return:
    """
    if show_logs:
        logger.debug("运行命令：[ {cmd} ], 工作目录：{cwd}".format(
        cmd=cmd,
        cwd=cwd.resolve() if cwd else os.getcwd()))
    if not shell:
        # 解析环境变量和 user
        cmd_parts = shlex.split(cmd)
    else:
        cmd_parts = cmd

    result = subprocess.run(cmd_parts,
                            shell=shell,
                            input=input,
                            timeout=timeout,  # 超时时间可能会失效，这是 subprocess 的 bug
                            check=check,
                            cwd=str(cwd.resolve()) if cwd else None,
                            **kwargs)
    return result



@contextmanager
def cd(newdir: Union[Path, str]):
    """
    通过 with 上下文管理器来管理 current working directory

    ```python
    from utils import shell

    with shell.cd("xxx"):
        shell.run_cmd("ls -al")
    ```

    参考：https://stackoverflow.com/questions/431684/how-do-i-change-the-working-directory-in-python
    """
    prevdir = Path.cwd()
    os.chdir(Path(newdir).resolve().as_posix())
    try:
        yield
    finally:
        os.chdir(prevdir)
