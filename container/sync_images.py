# -*- encoding: utf-8 -*-
"""
从国外的 quay.io/gcr.io 等仓库拉取容器镜像，然后：
    1. 推送到个人的阿里云容器镜像仓库中
    2. 导出为 tgz 文件保存到本地

要求先安装好 skopeo 工具，它比 docker pull/tag/push 更好用。

另外腾讯开源了一个更企业级的镜像迁移工具，也可以考虑：https://github.com/tkestack/image-transfer
=====================
导入所有 tgz 镜像文件的 shell 命令：
for img in images/*; do docker load -i $img; done

传输到某主机并导入所有 tgz 镜像的 shell 命令：
tar c images | ssh root@<host> "tar x; for img in images/*; do docker load -i \$img; done"

更复杂的操作，请使用 python 脚本或者 ansible 处理。
"""

import os
import re
import subprocess
from pathlib import Path


# 源镜像仓库：镜像列表
REPO_IMAGES_DICT = {
    # quay.io 目前国内拉取速度已经很快了，不需要手动同步。
    # "quay.io": (
    # ),
}

# 我的阿里云容器镜像仓库
MY_ALIYUN_REPO = "registry.cn-shanghai.aliyuncs.com/ryan4yin"

TGZ_DIR = Path(__file__).parent / "images"
TGZ_DIR.mkdir(exist_ok=True)


# 设置代理（环境变量）
os.environ.update({
    "HTTP_PROXY": "http://<proxy-host>:8889",
    "HTTPS_PROXY":"http://<proxy-host>:8889",
    # 本地及阿里云镜像仓库，不走代理
    "NO_PROXY":"localhost,127.0.0.1,registry.cn-shanghai.aliyuncs.com",
})


def sync_images(src_repo, dest_repo, image_tags):
    for tag in image_tags:
        # 阿里云镜像仓库不支持嵌套路径
        # tag = tag.replace("/", "_")

        src_tag = f"{src_repo}/{tag}"
        dest_tag = f"{dest_repo}/{tag}"
        image_archive_name = re.sub(r"[/:-]", "_", tag) + ".tgz"
        image_archive_path = TGZ_DIR / image_archive_name

        print(f">>> save image: '{src_tag}' to '{image_archive_path}'")
        subprocess.run(["skopeo", "copy", f"docker://{src_tag}", f"docker-archive:{image_archive_path}"])

        print(f">>> upload '{image_archive_path}' to '{dest_tag}'")
        subprocess.run(["skopeo", "copy", f"docker-archive:{image_archive_path}", f"docker://{dest_tag}"])


def main():
    for src_repo, image_tags in REPO_IMAGES_DICT.items():
        sync_images(src_repo, MY_ALIYUN_REPO, image_tags)


if __name__ == "__main__":
    main()
