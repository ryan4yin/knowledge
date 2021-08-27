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


## 依赖管理

Go 语言的依赖管理分成两种情况

### 1. 全局安装（安装到 GOPATH 下）

这个模式，通常用于安装系统全局的 tools，比如 [golang/tools](https://github.com/golang/tools) 中的官方工具，或者别的二进制程序。

两个命令介绍如下：

1. `go install`: 下载依赖源码到 `$GOPATH/src` 目录下。然后编译源码
   1. 编译出的静态链接库（`xxx.a`）将被放到 `$GOPATH/pkg` 目录下
   2. 编译得到的可执行文件将会被放到 `$GOROOT/bin` 目录下。
2. `go get -u`: 首先从网络上下载源码，然后 `install` 它。
   1. `-u` 表示更新到最新版本


### 2. Module-aware 模式

在 `GOMODULE111=on` 时，如果当前工作目录或者任意父文件夹中存在 `go.mod`， Module-aware 模式就会自动激活。

这个模式下，`go get` 有不同的功用，它首先解析并添加依赖到 `go.mod`，然后再 `install` 这些依赖。

`go get` 支持版本号或者 commit，几种示例用法如下：

```shell
go get github.com/gorilla/mux@latest    # same (@latest is default for 'go get')
go get github.com/gorilla/mux@v1.6.2    # records v1.6.2
go get github.com/gorilla/mux@e3702bed2 # records v1.6.2
go get github.com/gorilla/mux@c856192   # records v0.0.0-20180517173623-c85619274f5d
go get github.com/gorilla/mux@master    # records current meaning of master
```

此外还有一系列 go mod 相关命令：

- `go mod download`: 下载项目的所有依赖
- `go mod tidy`: 添加缺失的依赖项，删除未使用的依赖项

## 参考

- [Go语言核心36讲 - 目录](https://time.geekbang.org/column/intro/112)
- [7 days golang programs from scratch](https://github.com/geektutu/7days-golang)
- [go project-layout](https://github.com/golang-standards/project-layout)