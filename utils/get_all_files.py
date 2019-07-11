# -*- coding:utf-8 -*-
from pathlib import Path

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
    
