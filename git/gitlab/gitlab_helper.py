"""
对所有（有权限的） gitlab 仓库进行批量操作：

1. clone 所有仓库，文件夹路径和 gitlab path 完全对应
2. 导入导出所有仓库
3. 批量删除仓库（危险操作）

======
需要提前安装依赖：python-gitlab

======
用法示例：

```python3
# 克隆 `ryan4yin` 路径下的所有仓库

from pathlib import Path
gh = GitlabHelper("http://gitlab.svc.local", private_token="<token>", ssl_verify=False)
group = gh.get_group("ryan4yin")

# 将所有仓库克隆到 codes 文件夹下
gh.clone_projects_under_group(Path("codes"), group)
```

```python3
# 拷贝 repos 列表中的仓库到新路径下（既不是克隆，也不是迁移）

repos = [
    "repo_a",
    "repo_b",
    "repo_c",
]
old_group_path = "old_group"
new_group_path = "new_group"

gh = GitlabHelper("http://gitlab.svc.local", private_token="<token>")

for repo in repos:
    project = gh.get_project(old_group_path + "/" + repo)
    new_path = new_group_path + "/" + repo
    print("copy project:", new_path)
    stream = gh.export_groject(project)
    gh.import_project(stream, new_path, overwrite=False)
```

```python3
# 打印出给定 Group 中所有仓库的完整路径

gh = GitlabHelper("http://gitlab.svc.local", private_token="<token>", ssl_verify=False)
group = gh.get_group("ryan4yin")

paths = [project.path_with_namespace for project in gh.get_projects_under_group(group)]
Path("git-repo.list").write_text(
    "\n".join(paths)
)
```
"""

import time
import shlex
import subprocess

from io import BytesIO
from pathlib import Path
from typing import Union

import gitlab


class NotFoundException(RuntimeError):
    """未找到"""
    def __init__(self, msg):
        super().__init__(self, msg)
        self.msg = msg

class TooMuchException(RuntimeError):
    """找到过多的对象"""
    def __init__(self, msg):
        super().__init__(self, msg)
        self.msg = msg

class DuplicatedException(RuntimeError):
    """重复操作"""
    def __init__(self, msg):
        super().__init__(self, msg)
        self.msg = msg


class GitlabHelper:
    def __init__(self, url, private_token, **kwargs):
        """
        使用 token 登录 Gitlab
        """
        self.gl = gitlab.Gitlab(url, private_token, **kwargs)
        self.gl.auth()

    def get_project(self, path_or_id: Union[str, int]):
        """通过 git 项目的 path 或者 id，取得 project 对象

        示例：self.get_project("ryan4yin/devops")
        """
        return self.gl.projects.get(path_or_id)
    
    def get_group(self, path_or_id: Union[str, int]):
        """通过 Group （文件夹）的 path 或者 id，取得 Group 对象

        示例：self.get_group("ryan4yin")
        """
        return self.gl.groups.get(path_or_id)
    
    def get_projects_under_group(self, group, recursive=True):
        """列出给定 group （文件夹）中的所有 Git 项目。
        :param recursive: 是否递归到子文件夹中查找 Git 项目
        """
        for project in group.projects.list(all=True):
            yield project
        
        if not recursive:
            return
        
        for sub_group in group.subgroups.list(all=True):
            print("down into subgroup: ", sub_group.full_path)
            next_group = self.gl.groups.get(sub_group.full_path)
            yield from self.get_projects_under_group(next_group, recursive=recursive)

    def clone_projects_under_group(self, local_dir: Path, group, recursive=True):
        """
        clone 所有仓库到 local_dir 下，文件夹路径和 gitlab path 完全对应

        已经存在的仓库则忽略
        """
        for project in self.get_projects_under_group(group, recursive=recursive):
            git_path = local_dir.resolve() / project.path_with_namespace
            if git_path.exists():
                print(f"{git_path} 已存在，跳过 clone")
            
            parent_dir = git_path.parent
            parent_dir.mkdir(parents=True, exist_ok=True)  # 创建父文件夹

            # 克隆代码
            cmd = f"git clone '{project.ssh_url_to_repo}'"
            # cmd = f"git clone '{project.http_url_to_repo}'"  # 使用 http 协议
            print("="*50)
            print(f"work_dir: {parent_dir},command: {cmd}")
            subprocess.run(shlex.split(cmd), cwd=parent_dir)  # 失败不报错

    def export_project(self, project):
        """
        导出给定的 project 为 tar.gz 流对象
        """
        def wait_until_export_finished(export):
            export.refresh()
            # Wait for the 'finished' status
            while export.export_status != 'finished':
                time.sleep(1)
                export.refresh()

        def get_export_stream(export):
            bio = BytesIO()
            export.download(streamed=True, action=bio.write)
            bio.seek(0)
            return bio

        # 导出 project
        export = project.exports.create()
        # 等待导出完毕
        wait_until_export_finished(export)
        # 下载 tar.gz 流
        stream = get_export_stream(export)
        return stream

    def export_projects_under_group(self, group, recursive=True):
        """
        将给定 group 下的所有 git 项目导出为 tar.gz
        :param recursive: 是否递归导出 sub_group（子文件夹）下的 git 项目？
        :return : 返回一个迭代器，每一次迭代得到一个 (project, stream) 元组。
            project 为 git 项目的对象，stream 为导出的 tar.gz 流对象。
        """
        for p in self.get_projects_under_group(group, recursive=recursive):
            print("export project: ", p.path_with_namespace)
            p = self.gl.projects.get(p.id)

            yield p, self.export_project(p)

    def import_project(self, stream, project_full_path, overwrite=False):
        """
        将导出的 tar.gz 导入 Gitlab 中。
        """
        full_path = Path(project_full_path)
        namespace = full_path.parent.as_posix() # 父文件夹路径
        name = full_path.name # 项目名称

        output = self.gl.projects.import_project(
                stream,
                name=name,  # 显示名称（仅页面显示用）
                namespace=namespace, # Group （父文件夹）的完整路径
                path=name,  # 路径中的仓库名称（真正的仓库名）
                overwrite=overwrite
            )
        
        # Get a ProjectImport object to track the import status
        project_import = self.gl.projects.get(output['id'], lazy=True).imports.get()
        while project_import.import_status != 'finished':
            time.sleep(1)
            project_import.refresh()

        print(f"finish project import: {project_full_path}")

    def protect_branch_under_group(self, group, branch: str, recursive=True):
        """
        遍历给定 Group 下的所有仓库，将它们的某个分支设为保护分支。
        普通开发者(Developer) 不允许推送或者合并保护分支
        """
        for p in self.get_projects_under_group(group, recursive=recursive):
            print(f"将 {p.path_with_namespace} 的 {branch} 分支，设为保护分支")
            p = self.gl.projects.get(p.id)
            p.branchs.get(branch).protect()

    def delete_projects_under_group(self, group, recursive=False):
        """危险操作！！！
        删除给定 group （文件夹）下的所有 git 项目
        :param recursive: 是否递归删除 sub_group（子文件夹）下的 git 项目？
        """
        for project in self.get_projects_under_group(group, recursive=recursive):
            print("delete project: ", project.path_with_namespace)
            input("enter to confirm>")
            self.gl.projects.get(project.id).delete()

