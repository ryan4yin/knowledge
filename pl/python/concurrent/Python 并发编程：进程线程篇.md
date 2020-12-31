Python 提供了 threading 和 multiprocessing 用于编写多线程/多进程程序。

## 简单的并发编程

如果你不需要在多个进程/线程之间传递数据，那么 Python 的并发编程可以说是很简单。而且多进程与多线程编程的 API 基本一模一样。

```python3
import threading

def function(i):
    """需要并发运行的任务"""
    time.sleep(0.1)  # 模拟任务耗时
    print (f"function called by Thread: {i}")
    return

threads = []

for i in range(5):
    t = threading.Thread(target=function , args=(i, ))  # 构造 Thread 实例
    threads.append(t)
    t.start()  # 启动线程（主线程不会等待）

# 这里主线程可以干些别的事（并发地）
# ...

# 现在主线程没事干了，它会等待子线程全部完成，然后退出。
```

上面的代码会启动五个并发线程，同时主线程也能并发地执行一些别的任务。

要把上面的代码改成多进程，可以说是相当简单：

```python3
# -*- coding: utf-8 -*-

import multiprocessing

def function(i):
    """需要并发运行的任务"""
    time.sleep(0.1)  # 模拟任务耗时
    print (f"function called in Process: {i}")
    return

if __name__ == '__main__':
    Process_jobs = []
    for i in range(5):
        p = multiprocessing.Process(target=foo, args=(i,))
        Process_jobs.append(p)
        p.start()
```

可以看到，只要简单地将类 `threading.Thread` 换成 `multiprocessing.Process` 就行了。 这两个类的构造器参数没有任何差别：
- `threading.Thread(group=None, target=None, name=None, args=(), kwargs={}, *, daemon=None)`
- `multiprocessing.Process(group=None, target=None, name=None, args=(), kwargs={}, *, daemon=None)`

## 需要通信的并发编程

但是一旦需要在异步任务间通信，问题就变得复杂了。
对于多线程，我们需要使用各种同步机制来确保对共享变量的修改是顺序进行的。
对于多进程，我们需要使用管道/队列来通信。




待续

## 用线程还是用进程？

有时候我们无法确定一个任务是 IO 密集型还是计算密集型，也就无法确定该使用线程还是进程，这时 **multiprocessing.dummy** 帮我们解决了这个选择困难症。

**multiprocessing.dummy** 的 API 完全等同于 multiprocessing 包, 但是它实际上是一个 threading 库的封装。（也就是说是多线程的）

**如果一个功能你不确定用多进程还是多线程，那就用 multiprocessing 的 API 写，然后用 dummy 的多线程和原生的多进程比较，哪个快就用哪个。**这样需要改的只是一个导包语句。 


## 参考

- [multiprocessing](https://docs.python.org/3/library/multiprocessing.html)
- [threading](https://docs.python.org/3/library/threading.html)