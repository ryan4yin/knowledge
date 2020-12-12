# -*- coding: utf-8 -*-

import os
import shutil
import tarfile
from io import BytesIO
from pathlib import Path
from typing import IO


def get_all_files(path: Path, recursion=True):
    """
    获取指定目录下的所有文件
    path: 路径
    recursion: 是否递归遍历子文件夹
    """
    for f in path.iterdir():
        if f.is_file():
            yield f
        else:  # f.is_dir() == True
            yield from get_all_files(f, recursion=recursion)


def rm_target(path: Path):
    """移除文件/文件夹"""
    path = path.resolve()
    if path.exists():
        if path.is_dir():
            shutil.rmtree(path=str(path))
        else:
            os.remove(str(path))


def move(src_path: Path, dest_path: Path):
    """移动文件/文件夹"""
    os.rename(str(src_path), str(dest_path))  # hhh


def tar_files(src_path: Path, c_type="gz", output_path: Path = None, get_stream: bool = False):
    """压缩一个文件/文件夹"""
    io_obj = BytesIO()
    with tarfile.open(fileobj=io_obj, mode='w:{}'.format(c_type)) as tar_obj:
        tar_obj.add(str(src_path.resolve()), arcname=src_path.name)

    io_obj.flush()
    io_obj.seek(0)
    if get_stream:
        return io_obj
    elif output_path:
        with output_path.open("wb") as f:
            f.write(io_obj.read())
    else:
        raise KeyError("必须指定 output_path 或者 get_stream")


