"""
使用方式：python gitall.py pull
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
        git_root_dir = git_dir.parent

        cmd = ["git", *args]
        print(f"command: {cmd}, work_dir: {git_root_dir}")
        subprocess.run(cmd, cwd=git_root_dir)

if __name__ == "__main__":
    args_for_git = sys.argv[1:]
    gitall(args_for_git)
