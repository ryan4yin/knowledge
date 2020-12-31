# Go 语言

## Go 环境变量

1. `$GOPATH`: Go 的工作目录，和 Python 的包导入路径 `$PYTHONPATH` 类似但含义有区别。
    - 它的默认值为 `$HOME/go`
    - $GOPATH 下通常有三个约定好的子目录：src pkg bin
    - 目前依赖管理已经改用 go modules 实现，依赖缓存存放在 
    - 和系统的 $PATH 变量一样，$GOPATH 也支持使用同样的语法设置多个目录，靠前的目录将被优先检索。
1. $GOROOT: Go SDK 的安装位置

## Go 语言代理

设置国内代理，否则无法拉取依赖：

```shell
go env -w GOPROXY=https://goproxy.cn,direct
go env -w GOPRIVATE=*.svc.local
```

## Go 常用命令


### 依赖管理

全局安装（安装到 GOPATH 下）：

1. `go install`: 下载依赖源码到 `$GOPATH/src` 目录下。然后编译源码
   1. 编译出的静态链接库（`xxx.a`）将被放到 `$GOPATH/pkg` 目录下
   2. 编译得到的可执行文件将会被放到 `$GOROOT/bin` 目录下。
2. `go get`: 首先从网络上下载源码，然后 `install` 它。

在项目的依赖管理中，上述两个命令现在基本都可以使用 `go mod` 替换了，但是在系统中安装某些命令行工具时，还是经常会用到 `go get -u xxx`。
这就像我写 python 项目通常用 `poetry` 替换掉 `pip`，但是安装系统工具时又经常使用 `pip` 一样。


使用 go modules 安装（针对项目）：

3. `go mod`: 提供了一整套完善的依赖管理机制，和 python-`poetry`/node-`npm` 有点相似。


## 参考

- [Go语言核心36讲 - 目录](https://time.geekbang.org/column/intro/112)

