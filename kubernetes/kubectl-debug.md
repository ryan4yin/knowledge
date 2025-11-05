# kubectl debug

## 基础的网络调试功能

tcpdump 啊 grpcurl 啊啥的，这个略过不介绍了，具体可以看看这个 netshoot 容器的 README: <https://github.com/nicolaka/netshoot>

## Check main 容器的 Env / FilePath

首先使用如下命令启动 debug 容器：

```bash
kubectl debug -it --image=nicolaka/netshoot -it --target=main -n <namespace> <pod>
```

这样 debug 容器会跟 main 容器共用 process namespace, 可通过如下方法查看 main 进程的各种信息：

```bash
# 查看 PID 1 的 root file system
ls /proc/1/root/

# 查看 PID 1 的环境变量
tr '\0' '\n' < /proc/1/environ
```


## 使用 copy-to 

有时候可能因为一些原因，在 Pod 原地进行调试会比较困难，譬如：

- Pod 限制了不允许用 `root` 权限，无法临时安装工具、查看其他进程的信息
  - 可通过 copy-to 临时提升权限或放宽安全限制，譬如修改 `priviledged: true`, `securityContext` 等。
- Pod 无法启动或持续崩溃
  - 可通过 copy-to 修改启动命令与参数、容器镜像或环境变量，使容器保持运行，方便诊断
- 安全问题：在生产环境中，直接调试运行中的 Pod 是很危险的行为。

示例：

```bash
kubectl debug pod/myapp --copy-to=myapp-debug

# 允许读写 Root FS
kubectl patch pod/myapp-debug --type=json \
  -p='[{"op":"remove","path":"/spec/securityContext/readOnlyRootFilesystem"}]'

#  或者直接去掉 Pod 级的 securityContext
kubectl patch pod myapp-debug --type=json \
  -p='[{"op":"remove","path":"/spec/securityContext"}]'

#  再替换主容器镜像和启动命令
kubectl patch pod myapp-debug --type=json \
  -p='[{"op":"replace","path":"/spec/containers/0/image","value":"alpine:latest"},\
       {"op":"replace","path":"/spec/containers/0/command","value":["sh","-c"]},\
       {"op":"replace","path":"/spec/containers/0/args","value":["sleep 10000000"]}]'

kubectl attach -it myapp-debug -c myapp
```

## 退出与清理

debug container 会自动保留，如果想彻底删除：

```bash
kubectl patch pod -n app <pod> --type='json' \
  -p='[{"op": "remove", "path": "/spec/ephemeralContainers"}]'
```

