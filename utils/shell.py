# -*- coding: utf-8 -*-


import os
import shutil
import shlex
import subprocess
from pathlib import Path

import logging

logger = logging.getLogger(__name__)

"""
（使用 shell）调用其他命令行程序的包
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
    :param cmd: 命令字符串
    :param shell: 是否使用 shell 运行命令
    :param input: 标准输出
    :param timeout: 命令超时时间
    :param check: 如果命令失败，是否抛出异常？
    :param show_logs: 是否输出详细日志
    :param cwd: 命令运行前，将工作路径切换到 cwd 指定的位置
    :return:
    """
    if not shell:
        # 解析环境变量和 user
        cmd_parts = shlex.split(cmd)
        if show_logs:
            logger.debug("运行命令：{cmd_parts}, 工作目录：{cwd}".format(
                cmd_parts=cmd_parts,
                cwd=cwd.resolve() if cwd else os.getcwd()))
    else:
        if show_logs:
            logger.debug("运行 shell 命令：{cmd}, 工作目录：{cwd}".format(
                cmd=cmd,
                cwd=cwd.resolve() if cwd else os.getcwd()))
        cmd_parts = cmd

    result = subprocess.run(cmd_parts,
                            shell=shell,
                            input=input,
                            timeout=timeout,  # 超时时间可能会失效，这是 python 的 bug
                            check=check,
                            cwd=str(cwd.resolve()) if cwd else None,
                            **kwargs)
    return result
