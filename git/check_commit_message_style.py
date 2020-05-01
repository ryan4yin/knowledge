#!/usr/bin/env python3

"""
Git Server Hooks: pre-receive

检查 Git Commit Message 的格式是否符合 Angular Style
"""

import sys
import shlex
import subprocess

import re

commit_types = {
    "feat": "新特性",
    "fix": "修复 bug",
    "docs": "文档修改",
    "style": "代码格式修改（如代码格式化）",
    "refactor": "代码重构，既不修复 bug，也没有添加新特性的重构。",
    "perf": "性能优化",
    "test": "测试用例修改",
    "chore": "琐事，比如修改构建流程、更新/增删依赖等等",
    "revert": "手动回退修改"
}

commit_types_msg = '\n'.join(f'- {tp}: {desc}' for tp, desc in commit_types.items())

commit_msg_format = f"""
{'='*10}Commit Message 格式说明{'='*10}
<修改类型>(<影响范围>): <主题>
<--空行-->
[正文]
<--空行-->
[页脚]

{'-'*40}
其中必需部分：<修改类型>: <主题>
(<影响范围>)可省去，或写成 (*) 的形式
{'-'*40}
修改类型可选项：
{commit_types_msg}
{'-'*40}
修改最新 Commit Message 的命令如下:
git commit --amend -m "<修改类型>(<影响范围>): <主题>"
{'-'*40}
提交信息举例：https://github.com/angular/angular.js/commits/master
提交规范：https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#-git-commit-guidelines
{'='*10}Commit Message 格式说明{'='*10}
提交失败！详细错误请往上查看。
"""


def check_commit_msg(commit_id, commit_msg):
    """
    返回 boolean，表示是否通过检查

    暂时只检查第一行
    """
    lines = commit_msg.splitlines()
    print(f"提交ID：'{commit_id}', 提交信息（首行）: '{lines[0]}'")

    # 忽略掉 Revert 和 Merge 信息（git 自动生成的 commit message）
    for type_ in ("Revert ", "Merge "):
        if commit_msg.startswith(type_):
            return
    
    if ":" not in lines[0]:
        print("提交信息格式不正确！第一行需符合格式：<修改类型>(<影响范围>): <主题>")
        raise RuntimeError()

    type_scope, subject = commit_msg.split(":", maxsplit=1)

    # 验证 type 是否正确
    type_ = re.sub(r"\(.*\)", "", type_scope)
    if type_ not in commit_types.keys():
        print(f"<修改类型> 不正确，'{type_}' 不是可选类型之一！")
        raise RuntimeError()


def iter_commit_msg(parent_commit_id: str, latest_commit_id: str):
    """迭代所有的提交记录，从最新的提交开始"""
    print(f"新增提交记录范围：{parent_commit_id}..{latest_commit_id}")
    if parent_commit_id == "0" * len(parent_commit_id):  # 暂时不清楚这个 parent_commit_id 全为 0 是个什么情况
        # -1 表示仅输出 latest_commit_id 对应的提交信息
        cmd = shlex.split(f"git log -1 {latest_commit_id} --pretty=format:%h---%s")
    else:
        cmd = shlex.split(
            f"git log {parent_commit_id}..{latest_commit_id} --pretty=format:%h---%s")

    result = subprocess.run(
        cmd, check=True, capture_output=True, encoding='utf-8')

    for line in result.stdout.splitlines():
        commit_id, commit_msg = line.split("---", maxsplit=1)
        yield commit_id, commit_msg


def check_it():
    parent_commit_id, latest_commit_id, branch = input().split(" ")

    # 允许 branch/tag 的删除操作
    if latest_commit_id == "0" * len(latest_commit_id):
        return

    # 暂时只检查最新的一次提交信息
    commit_id, commit_msg = next(iter_commit_msg(
        parent_commit_id, latest_commit_id))
    check_commit_msg(commit_id, commit_msg)  # 未通过检查



def main():
    try:
        check_it()
    except Exception as e:
        print(commit_msg_format)
        sys.exit(-1)
    else:
        print(f"{'='*10}Commit Message 检测通过{'='*10}")


if __name__ == "__main__":
    main()
