# Go 语言

## Go 环境变量

可通过 `go env` 查看所有 Go 环境变量。

1. `$GOPATH`: Go 的工作目录，和 Python 的包导入路径 `$PYTHONPATH` 类似但含义有区别。
    - 它的默认值为 `$HOME/go`
    - $GOPATH 下通常有三个约定好的子目录：src pkg bin
    - 目前依赖管理已经改用 go modules 实现，依赖缓存都存放在 `$GOPATH/pkg` 中
    - 和系统的 `$PATH` 变量一样，`$GOPATH` 也支持使用同样的语法设置多个目录，靠前的目录将被优先检索。
2. `$GOROOT`: Go SDK 的安装位置，通常安装在 `/usr/local` 里面
   1. 包含了标准库、编译器、链接器、pprof 性能测试工具等等

## Go 语言代理

设置国内代理，否则无法拉取依赖：

```shell
# 设置使用七牛云代理地址
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


## 最佳实践

- 应该使用 make 为引用类型进行空间预分配
- defer 的使用
  - 主要用来管理上下文：比如 IO 句柄的自动关闭
  - [尽量不要使用 defer 来自动解锁](https://segmentfault.com/a/1190000019490834)，因为性能比较差。应该手动调用 `Unlock`!
- **不要使用 「 _ 」 丢弃任何返回的 err 错误**！要么把 err 传递到上层调用，要么使用 log 记录下来
  - 直接丢弃 err 会导致错误被隐藏，排查错误时就两眼一抹黑。
- 应该使用 `strings.Builder` 或者 `strings.Join` 拼接字符串
   - 因为字符串是不可变对象，直接用 + 拼接会创建出大量无用对象，浪费大量内存
  - 写过 java 的都应该很熟悉，写过 Python 的应该也知道要用 `''.join()`
- 对于并发编程中需要频繁分配内存的场景（比如频繁反序列化 Json），可以考虑使用 `sync.Pool`，来降低向内核申请内存的频率，提升性能。
- [谨慎关闭 channel，避免触发 panic](https://juejin.cn/post/7033671944587182087)
  - 应该只在发送端关闭 channel（避免往已关闭的 channel 发送数据导致 panic）
  - 存在多个发送者时不要关闭发送者 channel，而是使用专门的 stop channel
  - 在参数类型中，使用 `chan<-` 与 `<-chan` 指定 channel 发送方向，避免关闭错误的 channel

### Goroutine 最佳实践

#### `sync.Once`

提供了一个线程安全的单次执行接口，常用于单例模式或者初始化的场景。举例如下：

```go
package main
import (
    "sync"
)
type singleton struct {}
var instance *singleton
var once sync.Once
func GetInstance() *singleton {
    once.Do(func() {
        instance = &singleton{} // 只会执行一次，后续调用该方法不会执行
    })
    return instance
}
```

#### sync/atomic 原子操作

在并发场景下，如果需要对一个整形变量进行修改，最好使用 atomic 而不是 sync/mutex , sync.atomic 的实现原理大致是向 CPU 发送对某一个块内存的 LOCK 信号，然后就将此内存块加锁，从而保证了内存块操作的原子性。这种对 CPU 发送信号对内存加锁的方式，比 sync.Mutex 这种在语言层面对内存加锁的方式更底层，因此也更高效。

atomic 支持如下几种类型的：int32, int64, uint32, uint64, uintptr, unsafe.Pointer。这些原子操作函数有以下 5 种：增减（Add），存储（Store），载入（Load），交换（Swap），比较并交换（CompareAndSwap）。

```go
package main
import (
    "fmt"
"sync"
    "sync/atomic"
)
func main() {
    var value int64
    var wg sync.WaitGroup
	wg.Add(2)
    fun := func(count int) {
        for index := 0; index < count; index++ {
            atomic.AddInt64(&value, 1)  // not value++
        }
	wg.Done() }
    go fun(100)
    go fun(100)
	wg.Wait()
    fmt.Printf("%v\n", value)
}
```

#### sync.map

并发情况下如果需要对 map 进行操作，优先考虑使用 sync.map 而不是对 map 进行加锁，无论是互斥锁还是读写锁，相较于 sync.map 性能都是差很多的
Sync.map 核心是读写分离与原子操作，底层会有两个 map: 一个 readonly，一个被称为 dirty.

大概的原理：

- 通过 read 和 dirty 两个字段将读写分离，读的数据存在只读字段 read 上，将最新写入的数据则存在 dirty 字段上
- 读取时会先查询 read，不存在再查询 dirty，如果在dirty里查到了则记misses++。写入时则只写入 dirty。
- 读取 read 并不需要加锁，而读或写 dirty 都需要加锁
- 另外有 misses 字段来统计 read 被穿透的次数（被穿透指需要读 dirty 的情况），超过一定次数则将 dirty 数据同步到 read 上
- 对于删除数据则直接通过标记来延迟删除

```go
var ma sync.Map                //无需初始化
ma.Store("key", "value")       // 存储
ma.Delete("key")               // 删除
ma.LoadOrStore("key", "value") // 获取值。如果不存在则存储
ma.Load("key") // 读取
// 遍历
ma.Range(func(key, value interface{}) bool{
  fmt.Println(key, value)
  // 如果返回 false 则退出循环
  return true
})
```

#### 其他锁的优化

TODO

#### 协程池

对于需要频繁创建协程的业务场景，应尽可能使用协程池，重复利用资源，减少内存开销。
比如海量 Url 的连通性监控，每个 url 开辟一个协程不太现实，此时就需要引入协程池共享协程。

官方库并未提供协程池，如下是一个比较流行的实现：

- https://github.com/panjf2000/ants

### json 转 struct 工具

在日常开发中，尤其是微服务场景下，经常会碰到需要解析接口返回的 json 数据。
每一次都需要手工去构造一个结构体，太过繁琐而且难免会出错。推荐使用如下网站，将目标 json 复制上去就能自动生成对应的 Struct.

- https://mholt.github.io/json-to-go/ 

注意转换完后一定要确认一遍结果，不要直接闭眼 Copy. 比如有些字段可能就需要手动加上 required 等额外的属性。

### 尽量避免使用 panic

这是一个基本上所有语言都通用的最佳实践：强制退出程序的指令只应该用在程序最外部的入口方法里！
而内部方法应该抛出异常，或者通过其他方法把错误传递出去。

生产环境中应尽可能避免 panic，panic/recover 不是最佳的错误处理策略。仅当发生不可恢复的事情（例如：nil 引用），程序才必须 panic ，其他场景还是应该规规矩矩地 `return nil, err`.

### Goroutine 泄漏问题

Channel 可能会引发 goroutine 泄漏。

泄漏的原因是 goroutine 操作 channel 后，处于发送或接收阻塞状态，而 channel 处于满或空的状态，一直得不到改变。同时，垃圾回收器也不会回收此类资源，进而导致 gouroutine 会一直处于等待队列中，不见天日。
另外，程序运行过程中，对于一个 channel，如果没有任何 goroutine 引用了，gc 会对其进行回收操作，不会引起内存泄漏。

TODO

## 参考

- [Go语言核心36讲 - 目录](https://time.geekbang.org/column/intro/112)
- [7 days golang programs from scratch](https://github.com/geektutu/7days-golang)
- [go project-layout](https://github.com/golang-standards/project-layout)