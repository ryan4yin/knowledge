"""
在当前文件夹内的所有 Git 仓库中，批量执行某个 git 命令。

使用方式：

1. 批量拉取: python gitall.py pull
1. 还原仓库内容: python gitall.py checkout -- .
1. 批量清理未跟踪文件: python gitall.py clean -fxd
1. 批量提交: python gitall.py commit -m "xxx"
1. 批量推送: python gitall.py push origin master
"""
import sys
import subprocess
from typing import List
from pathlib import Path

def gitall(args: List[str]):
    """
    遍历当前文件夹下所有的 git 仓库，在每个仓库中执行某个 git 命令.
    """
    for git_dir in Path(".").glob("**/.git"):
        print("-"*50)  # 分隔线
        git_root_dir = git_dir.parent

        cmd = ["git", *args]
        print(f"command: {cmd}, work_dir: {git_root_dir}")
        subprocess.run(cmd, cwd=git_root_dir)

if __name__ == "__main__":
    args_for_git = sys.argv[1:]
    gitall(args_for_git)
