# coding: utf-8
import os
from operator import itemgetter
from urllib import parse
from urllib.parse import urljoin

import requests

import datetime as dt
# import maya
import logging

logger = logging.getLogger(__name__)

"""
对 Harbor 镜像仓库 RESTFul API 的封装
"""


class TagNotFoundError(RuntimeError):
    pass


class HarborApi(object):
    def __init__(self, username: str, password: str, hostname: str, ssl_verify: bool = True):
        api_base = urljoin(hostname, "/api")
        self.search_api = api_base + "/search?q={key_word}"
        self.projects_api = api_base + "/projects"
        self.repository_query_api = api_base + "/repositories?project_id={project_id}"
        # repo_name 一般为 "project_name/repo_name" 格式，必须做转义处理（因为中间有斜杠）
        self.repository_tags_api = api_base + "/repositories/{repo_name}/tags"
        self.repository_tag_api = self.repository_tags_api + "/{tag}"

        self.session = requests.Session()
        self.session.verify = ssl_verify  # 如果使用的是自签名证书，就需要将它设为 False
        self.session.headers = {
            "Accept": "application/json"
        }

        self.session.auth = (username, password)

    def get_all_projects(self, raise_exception: bool = True):
        """
        获取到 Harbor 仓库中的所有项目（projects）

        : return: 返回一个 projects 的列表，每个 project 是一个 dict 对象，格式如下：
            {
                "project_id": 36,
                "owner_id": 1,
                "name": "cache",  # project_name
                "creation_time": "2019-09-02T11:18:49Z",
                "update_time": "2019-09-02T11:18:49Z",
                "deleted": false,
                "owner_name": "",
                "togglable": true,
                "current_user_role_id": 1,
                "repo_count": 17,
                "chart_count": 0,
                "metadata": {
                    "auto_scan": "false",
                    "enable_content_trust": "false",
                    "prevent_vul": "false",
                    "public": "true",
                    "severity": "low"
                }
            },
        """
        resp = self.session.get(self.projects_api)

        resp.raise_for_status()

        return resp.json()

    def get_all_repos(self, project_id: int, raise_exception: bool = True):
        """
        获取到对应项目下所有的镜像仓库

        return: 返回一个 repos 的列表，每个 repo 是一个 dict 对象，格式如下：
            {
                "id": 171,
                "name": "cache/baget",  # repo_name
                "project_id": 36,
                "description": "",
                "pull_count": 3,
                "star_count": 0,
                "tags_count": 1,
                "labels": [],
                "creation_time": "2019-10-10T05:41:11.773953Z",
                "update_time": "2019-11-26T10:27:53.348818Z"
            },
        """
        url = self.repository_query_api.format(project_id=project_id)
        resp = self.session.get(url)

        resp.raise_for_status()

        return resp.json()

    def get_all_tags(self, repo_name: str, raise_exception: bool = True):
        """获取到指定镜像仓库中所有的镜像标签
        
        repo_name 可能会带有斜杠符，需要做转义

        : return: tags 的列表，每个 tag 为一个 dict 对象，格式如下：
            {
                "digest": "sha256:0bf0b71dc9a6d511b755b0bcde0ffa177025a35206640f0f9007f44d8e15e4c2",
                "name": "20191216011311",  # tag_name
                "size": 8807569,
                "architecture": "amd64",
                "os": "linux",
                "os.version": "",
                "docker_version": "19.03.5",
                "author": "NGINX Docker Maintainers <docker-maint@nginx.com>",
                "created": "2019-12-16T01:13:17.575940636Z",
                "config": {
                    "labels": {
                        "maintainer": "NGINX Docker Maintainers <docker-maint@nginx.com>"
                    }
                },
                "signature": null,
                "labels": []
            },
        """
        repo_name = parse.quote(repo_name, safe="")
        url = self.repository_tags_api.format(repo_name=repo_name)
        resp = self.session.get(url)

        if raise_exception:
            resp.raise_for_status()
        return resp.json()

    def get_all_tags_sroted_by_created_time(self, repo_name: str, raise_exception: bool = True):
        """和 get_all_tags 返回内容基本一致，
        """
        tags: list = self.get_all_tags(repo_name, raise_exception=raise_exception)
        for tag in tags:
            # tag['time'] = maya.MayaDT.from_iso8601(tag['created'])

            # '2019-04-09T11:33:49.296960745Z'
            # # python 自带的解析函数，只能处理 6 位小数，下面截去多余的三位
            timestamp = tag['created'][:-4] + 'Z'
            tag['time'] = dt.datetime.strptime(timestamp, r'%Y-%m-%dT%H:%M:%S.%fZ')

        tags.sort(key=itemgetter('time'))  # 使用 time 键进行原地排序
        return tags
    
    def get_all_tags_sorted_by_tagname(self, repo_name: str):
        tags: list = self.get_all_tags(repo_name)
        tags.sort(key=itemgetter('name'))  # 使用 tag name 键进行原地排序
        return tags

    def get_latest_tags(self, repo_name: str, raise_exception: bool = True):
        """
        获取到所有 latest 标签对应的镜像，所拥有的其他标签

        通常镜像打包时，我们会被镜像添加两个标签：latest, 和一个时间戳标签
        """
        tags = self.get_all_tags_sroted_by_created_time(repo_name)
        try:
            latest_tag = next(filter(lambda t: t['name'] == "latest", tags))  # 找到 latest 标签
        except StopIteration:
            raise TagNotFoundError("未找到 latest 标签")

        for tag in tags:
            if tag['name'] == "latest":  # 跳过 latest 标签它自己
                continue
            if tag['digest'] == latest_tag['digest']:  # 返回所有和 latest 标签 hash 一致的其他标签
                yield tag

    def soft_delete_tag(self, repo_name: str, tag_name: str, raise_exception: bool = True):
        """通过 RESTFul API 软删除指定的镜像标签        
        这里删除后，还需要进行一次 GC，才能真正地清理出可用空间。
        
        repo_name 需要做转义
        """
        repo_name = parse.quote(repo_name, safe="")
        url = self.repository_tag_api.format(repo_name=repo_name, tag=tag_name)
        resp = self.session.delete(url)

        resp.raise_for_status()
