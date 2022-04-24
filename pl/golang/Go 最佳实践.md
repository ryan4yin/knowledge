## Go 最佳实践

- 应该使用 make 为引用类型进行空间预分配
- defer 的使用
  - 通常被用来管理上下文：比如 IO 句柄的自动关闭，加锁后的自动解锁
  - 虽然 defer 有性能损耗，但是 **defer 最大的功能是 panic 后依然有效。如果没有 defer，panic 后如果程序被 recover 继续跑，就会导致 unlock 丢失，从而死锁**，针对这种场景就应该尽量使用 defer! 即使可能会损耗一点点性能。即便 defer 的性能问题真的无法接受，那也是之后做优化的事了（不要过早优化！）。
  - defer 在 return 语句更新了 result 数据后执行，因此可用于 check 甚至 update 函数最后的返回值。
  - 比如 defer 函数可用于 recover 可能存在的 panic，并修改返回的 err 错误内容
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

panic/recover 跟其他语言的 try-catch 机制有点类似，如果不处理的话会打印出异常调用栈。
但是 panic 的设计目的是不同的，**panic 被设计用于表示非常严峻的错误，当程序 panic 时，通常意味着程序存在 bug**.

仅当发生不可恢复的错误时（例如：nil 引用），程序才应该 panic ，其他场景如 IO 错误、配置错误、输入错误，仍然应该使用基于 `return nil, err` 的错误处理机制.

即使程序 panic 了，`defer` 的语句也会被执行，以确保资源被正确释放。

### os.Exit 与 log.Fatalf

一个基本上所有语言都通用的最佳实践：强制退出程序的指令如 `os.Exit` 只应该用在程序最外部的入口方法里！
而内部方法应该抛出异常，或者通过其他方法把错误传递出去。

因此 log.Fatalf 或者 os.Exit 只应该在最外部的 main 函数中使用。

否则可能会因为程序强制退出，defer 语句被忽略，锁、IO 句柄等资源未被成功释放导致泄漏。


### Goroutine 泄漏问题

Channel 可能会引发 goroutine 泄漏。

泄漏的原因是 goroutine 操作 channel 后，处于发送或接收阻塞状态，而 channel 处于满或空的状态，一直得不到改变。同时，垃圾回收器也不会回收此类资源，进而导致 gouroutine 会一直处于等待队列中，不见天日。
另外，程序运行过程中，对于一个 channel，如果没有任何 goroutine 引用了，gc 会对其进行回收操作，不会引起内存泄漏。

TODO


## 参考

- [Go defer 会有性能损耗，尽量不要用？](https://segmentfault.com/a/1190000019490834)

