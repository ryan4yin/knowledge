# coding: utf-8

from operator import itemgetter
from urllib import parse
import requests

import datetime as dt
# import maya

import logging
logging.basicConfig(filename='harbor_clean.txt', filemode="w", level=logging.INFO)

logger = logging.getLogger(__name__)

"""
清理 Harbor 仓库的老镜像
"""


class HarborCleaner(object):
    delete_status = {
        200: "Delete tag successfully.",	
        400: "Invalid repo_name.",
		401: "Unauthorized.",
		403: "Forbidden.",
		404: "Repository or tag not found.",
    }

    def __init__(self, user: str, password: str, hostname: str, port: int, use_https=True):
        scheme = "https" if use_https else "http"
        api_base = f"{scheme}://{hostname}:{port}/api"
        self.search_api = api_base + "/search?q={key_word}"
        self.projects_api = api_base + "/projects"
        self.repository_query_api = api_base + "/repositories?project_id={project_id}"
        # repo_name 一般为 "project_name/repo_name" 格式，必须做转义处理（因为中间有斜杠）
        self.repository_tags_api = api_base + "/repositories/{repo_name}/tags"
        self.repository_tag_api = self.repository_tags_api + "/{tag}"

        self.session = requests.Session()
        self.session.verify = False  # 如果公司是使用自签名证书，不能通过 SSL 验证，就需要设置这个
        self.session.headers = {
            "Accept": "application/json"
        }

        self.session.auth = (user, password)


    def get_all_projects(self):
        resp = self.session.get(self.projects_api)
        
        success = resp.status_code == 200
        return {
            "success": success,
            "data": resp.json() if success else resp.text
        }

    def get_all_repos(self, project: dict):
        url = self.repository_query_api.format(project_id=project['project_id'])
        resp = self.session.get(url)

        success = resp.status_code == 200
        return {
            "success": success,
            "data": resp.json() if success else resp.text
        }

    def get_all_tags(self, repo: dict):
        """repo_name 需要做转义"""
        repo_name = parse.quote(repo['name'], safe="")
        url = self.repository_tags_api.format(repo_name=repo_name)
        resp = self.session.get(url)

        success = resp.status_code == 200
        return {
            "success": success,
            "data": resp.json() if success else resp.text
        }
    
    def get_tags_except_lastest_n(self, repo: dict, n: int):
        """获取除了最新的 n 个 tag 之外的所有 tags"""

        # 如果 镜像 tags 数小于 n+1，说明该镜像很干净，不需要做清理。
        if repo['tags_count'] <= n+1:  # +1 是因为 latest 是重复的 tag
            return []
        
        result = self.get_all_tags(repo)
        tags: list = result['data']
        for tag in tags:
            # tag['time'] = maya.MayaDT.from_iso8601(tag['created'])

            # '2019-04-09T11:33:49.296960745Z'
            # # python 自带的解析函数，只能处理 6 位小数，下面截去多余的三位
            timestamp = tag['created'][:-4] + 'Z'
            tag['time'] = dt.datetime.strptime(timestamp, r'%Y-%m-%dT%H:%M:%S.%fZ')

        tags.sort(key=itemgetter('time'))  # 使用 time 键进行原地排序
        return tags[:-n-1]  # expect the latest n tags, -1 是因为 latest 是重复的 tag
    
    def soft_delete_tag(self, repo: dict, tag: dict):
        """repo_name 需要做转义
        这里删除后，还需要进行一次 GC，才能真正地清理出可用空间。
        """        
        repo_name = parse.quote(repo['name'], safe="")
        url = self.repository_tag_api.format(repo_name=repo_name, tag=tag['name'])
        resp = self.session.delete(url)

        return {
            "success": resp.status_code == 200,
            "message": self.delete_status.get(resp.status_code)
        }

    def soft_delete_all_tags_except_latest_n(self, n):
        """从每个仓库中，删除所有的 tags，只有最新的 n 个 tag 外的所有 tags 除外"""
        res_projects = self.get_all_projects()
        if not res_projects['success']:
            logger.warning("faild to get all projects, message: {}".format(res_projects['data']))

        logger.info("we have {} projects".format(len(res_projects['data'])))
        for p in res_projects['data']:
            res_repos = self.get_all_repos(p)
            if not res_projects['success']:
                logger.warning("faild to get all repos in project: {}, message: {}".format(p['name'], res_repos['data']))

            logger.info("we have {} repos in project:{}".format(len(res_repos['data']), p['name']))
            for repo in res_repos['data']:
                logger.info("deal with repo: {}".format(repo['name']))

                old_tags = self.get_tags_except_lastest_n(repo, n)
                logger.info("we have {} tags to delete in repo: {}".format(len(old_tags), repo['name']))
                for tag in old_tags:
                    logger.info("try to delete repo:{}, tag: {}, create_time: {}".format(repo['name'], tag['name'], tag['created']))
                    result = self.soft_delete_tag(repo, tag)
                    if result['success']:
                        logger.info("success delete it.")
                    else:
                        logger.warning("delete failed!, message: {}".format(result['message']))


if __name__ == "__main__":
    # 1. 通过 harbor 的 restful api 进行软删除
    harbor_cleaner = HarborCleaner(
        user="admin",
         password="Admin123",
         hostname="reg.harbor.com",
         port=8321
    )
    harbor_cleaner.soft_delete_all_tags_except_latest_n(10)  # 每个镜像只保留最新的十个 tag

    # 2. 进行一次 GC，清除掉所有已软删除的 images
    # harbor 1.7+ 可以通过 restful api 进行在线 GC 或定期自动 GC。



