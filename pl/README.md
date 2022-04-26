# 编程语言相关

1. 编译运行环境的安装配置
1. 总结出来的的一些 utils 代码
2. 语言相关的笔记


## 语言的学习

除了 Go/Python/C/Rust/lua 这几个生产力语言的持续精进外，我每年还可以再学一点 PLT 理论，也学一些新的语言开拓视野。

目前我比较感兴趣的语言有：

- Kotlin: 又一个运行在 JVM 上的语言，替代 Java 的不二选择
- Ruby 系
  - Elixir: 走的 Erlang 函数式语言的路线，底层运行在 Erlang 的 BEAM 虚拟机上，特点是能提供超高并发
  - Crystal: 走的是跟 Go 一致的 CSP 并发模型路线，但是语法是 Ruby 的语法
- 学院派
  - idris/agda/haskell: 大佬们的玩具，先懂点 PLT 理论再接触吧


## 内存管理 - 堆内存与栈内存

- 堆内存：需要 GC，通过 指针/引用 来索引
  - 内存泄漏指的就是未手动释放堆内存，导致堆内存无法被回收
- 栈内存：不需要 GC，函数退出时栈内存就被自动销毁了

## 源码阅读

阅读源码时，如下几点可以帮助你更快更好地理解：

- 画体系结构图
- 做笔记
- 调试

## 练习项目

- [app-ideas](https://github.com/florinpop17/app-ideas)
- [project-based-learning](https://github.com/tuvtran/project-based-learning)
- [500lines](https://github.com/aosabook/500lines)


## 特定语言的源码阅读或者实践项目

算法：

- [TheAlgorithms](https://github.com/TheAlgorithms): 包含各种算法在各种语言中的实现！

rust:

- [kibi](https://github.com/ilai-deutel/kibi): text editor in <= 1024 lines of code.

c:

- [kilo](https://github.com/antirez/kilo): A text editor in less than 1000 LOC with syntax highlight and search.


go:

- [tinykv](https://github.com/tidb-incubator/tinykv)
- [tinysql](https://github.com/tidb-incubator/tinysql)
- [go 源码阅读笔记](https://github.com/cch123/golang-notes)

python:

- [tinydb](https://github.com/msiemens/tinydb)

设计模式：

- [python-patterns](https://github.com/faif/python-patterns)
- [go-patterns](https://github.com/tmrts/go-patterns)
- [rust patterns](https://github.com/rust-unofficial/patterns)
