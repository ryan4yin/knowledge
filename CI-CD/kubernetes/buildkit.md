# 使用 Buildkit

- 关注点
  - layer 及 directory 缓存复用
  - 多架构支持

Dockerfile for buildkit with ecr:

```Dockerfile
FROM moby/buildkit:v0.12.2

# https://github.com/awslabs/amazon-ecr-credential-helper/releases/tag/v0.7.1
RUN wget -O docker-credential-ecr-login https://amazon-ecr-credential-helper-releases.s3.us-east-2.amazonaws.com/0.7.1/linux-amd64/docker-credential-ecr-login \
    && chmod +x docker-credential-ecr-login \
    && mv docker-credential-ecr-login /usr/local/bin
```

```bash
# TODO set environment variables used below

# auth for aws ecr
echo '{ "credsStore": "ecr-login" }' > docker_config.json
# build by buildkit in docker
# note we need to use `image-manifest=true` to make it work, otherwise it will fail with 400 bad request
# cause it will try to push a manifest list to ecr, but ecr doesn't support manifest ordered list
docker run \
    --privileged \
    -v ${IMAGE_CONTEXT}:/tmp/work \
    -v $(pwd)/docker_config.json:/.docker/config.json \
    -e DOCKER_CONFIG=/.docker \
    -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
    -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
    --entrypoint buildctl-daemonless.sh \
    buildkit-ecr:v0.12.2 \
        build \
        --progress=plain \
        --frontend=dockerfile.v0 \
        --local context=/tmp/work \
        --local dockerfile=/tmp/work \
        --output type=image,name=${IMAGE}:v1,push=true \
        --export-cache type=registry,mode=max,image-manifest=true,ref=${IMAGE}:buildcache \
        --import-cache type=registry,ref=${IMAGE}:buildcache
```

- [buildkit](https://github.com/moby/buildkit)
- [buildkit-cli-for-kubectl](https://github.com/vmware-tanzu/buildkit-cli-for-kubectl)
