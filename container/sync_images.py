# -*- encoding: utf-8 -*-
"""
从国外的 quay.io/gcr.io 等仓库拉取容器镜像，然后：
    1. 推送到个人的阿里云容器镜像仓库中
    2. 导出为 tgz 文件保存到本地

使用此脚本的前提是：本机的 docker 会通过代理拉取镜像，设置方法参见本仓库的 docker 文档。

=====================
导入所有 tgz 镜像文件的 shell 命令：
for img in images/*; do docker load -i $img; done

传输到某主机并导入所有 tgz 镜像的 shell 命令：
tar c images | ssh root@<host> "tar x; for img in images/*; do docker load -i \$img; done"

更复杂的操作，请使用 python 脚本或者 ansible 处理。
"""

import re
import subprocess
from pathlib import Path


# 源镜像仓库：镜像列表
REPO_IMAGES_DICT = {
    "quay.io": (
        # rook-ceph v1.4.1 的镜像
        # "cephcsi/cephcsi:v3.1.0",
        # "k8scsi/csi-node-driver-registrar:v1.2.0",
        # "k8scsi/csi-provisioner:v1.6.0",
        # "k8scsi/csi-snapshotter:v2.1.1",
        # "k8scsi/csi-attacher:v2.1.0",
        # "k8scsi/csi-resizer:v0.4.0",

        # prometheus-operator 镜像
        "prometheus/alertmanager:v0.21.0",
        "prometheus/prometheus:v2.18.2",
        "coreos/prometheus-operator:v0.38.1",
        "coreos/prometheus-config-reloader:v0.38.1",
    ),
}

# 我的阿里云容器镜像仓库
MY_ALIYUN_REPO = "registry.cn-shanghai.aliyuncs.com/ryan4yin"

TGZ_DIR = Path(__file__).parent / "images"
TGZ_DIR.mkdir(exist_ok=True)


def sync_images(src_repo, dest_repo, image_tags):
    for tag in image_tags:
        # 阿里云镜像仓库不支持嵌套路径
        # tag = tag.replace("/", "_")

        src_tag = f"{src_repo}/{tag}"
        dest_tag = f"{dest_repo}/{tag}"

        print(f">>> pull image: {src_tag}")
        subprocess.run(["docker", "pull", src_tag])

        # print(f">>> rename image: {src_tag} => {dest_tag}")
        # subprocess.run(["docker", "tag", src_tag, dest_tag])

        # print(f">>> push image: {dest_tag}")
        # subprocess.run(["docker", "push", dest_tag])

        tgz_name = re.sub(r"[/:-]", "_", tag) + ".tgz"
        print(f">>> save image: {src_tag}")
        subprocess.run(f"docker save {src_tag} | gzip > {TGZ_DIR / tgz_name}", shell=True)


def main():
    for src_repo, image_tags in REPO_IMAGES_DICT.items():
        sync_images(src_repo, MY_ALIYUN_REPO, image_tags)


if __name__ == "__main__":
    main()
