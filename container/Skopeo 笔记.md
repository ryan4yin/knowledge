# [Skopeo](https://github.com/containers/skopeo) 笔记

在镜像重命名/迁移的应用场景中，可以使用 skopeo 替代掉以前使用 docker pull –> docker tag –> docker push 的操作。

使用 `docker` 来干这活，最大的问题是它一定要在本地解压镜像的 tar.gz 包，严重拖慢速度。而且要三条命令，不够精简。

`skopeo` 一行命令就能搞定，而且不会在本地解压镜像压缩包，速度会快很多。

安装方式略过，直接使用 yum/apt/pacman install 就 ok.

>注：本文的所有命令基本都跳过了内网 registry 的 tls 验证。但是如果有条件，还是建议先安装 ca 证书以保证安全性。

## 登录镜像仓库

skopeo 的身份认证配置的默认位置为 ` ${XDG_RUNTIME_DIR}/containers/auth.json`，如果该文件不存在，也会检查 docker 的默认配置 `$HOME/.docker/config.json`.

配置格式和 docker 一致。

```
# 登录内网 registry，不验证 tls 证书
docker login registry.svc.local --tls-verify=false
```

## 常用命令

### 1. skopeo copy

常用法举例：
```shell
# 将镜像从 quay.io 复制到内网 registry，不验证内网仓库的 tls 证书 
skopeo copy --dest-tls-verify=false \
  docker://quay.io/buildah/stable docker://registry.svc.local/test/buildah
  

# 将 registry 中的镜像改个名称(或者换个 project)，不验证内网仓库的 tls 证书
skopeo copy --src-tls-verify=false --dest-tls-verify=false \
  docker://registry.svc.local/test/buildah docker://registry.svc.local/test/buildah-stable

# 将镜像导出为 docker tar.gz 压缩包
skopeo copy docker://quay.io/buildah/stable docker-archive:buildah-stable.tgz

# 列出 registry 中某镜像的所有 tags（输出为 json 格式）
skopeo list-tags --tls-verify=false docker://registry.svc.local/test/buildah
```

## 参考文档

- [镜像搬运工 skopeo 初体验](https://blog.k8s.li/skopeo.html)
