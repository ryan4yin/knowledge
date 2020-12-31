>个人笔记，如有疏漏，还请指正。

使用多线程（threading）和多进程（multiprocessing）完成常规的并发需求，在启动的时候 start、join 等步骤不能省，复杂的需要还要用 1-2 个队列。
随着需求越来越复杂，如果没有良好的设计和抽象这部分的功能层次，代码量越多调试的难度就越大。

对于需要并发执行、但是对实时性要求不高的任务，我们可以使用 concurrent.futures 包中的 PoolExecutor 类来实现。

这个包提供了两个执行器：线程池执行器 ThreadPoolExecutor 和进程池执行器 ProcessPoolExecutor，两个执行器提供同样的 API。

>池的概念主要目的是为了重用：让线程或进程在生命周期内可以多次使用。它减少了创建创建线程和进程的开销，提高了程序性能。重用不是必须的规则，但它是程序员在应用中使用池的主要原因。

池，只有固定个数的线程/进程，通过 max_workers 指定。
1. 任务通过 executor.submit 提交到 executor 的任务队列，返回一个 future 对象。
    - Future 是常见的一种并发设计模式。一个Future对象代表了一些尚未就绪（完成）的结果，在「将来」的某个时间就绪了之后就可以获取到这个结果。
1. 任务被调度到各个 workers 中执行。但是要注意，**一个任务一旦被执行，在执行完毕前，会一直占用该 worker！**
    - **如果 workers 不够用，其他的任务会一直等待！**因此 PoolExecutor 不适合实时任务。

```python
import concurrent.futures
import time
from itertools import count

number_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

def evaluate_item(x):
    for i in count(x):  # count 是无限迭代器，会一直递增。
        print(f"{x} - {i}")
        time.sleep(0.01)


if __name__ == "__main__":
        # 进程池
        start_time_2 = time.time()

        # 使用 with 在离开此代码块时，自动调用 executor.shutdown(wait=true) 释放 executor 资源
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                # 将 10 个任务提交给 executor，并收集 futures
                futures = [executor.submit(evaluate_item, item) for item in number_list]

                # as_completed 方法等待 futures 中的 future 完成
                # 一旦某个 future 完成，as_completed 就立即返回该 future
                # 这个方法，使每次返回的 future，总是最先完成的 future
                # 而不是先等待任务 1，再等待任务 2...
                for future in concurrent.futures.as_completed(futures):
                        print(future.result())
        print ("Thread pool execution in " + str(time.time() - start_time_2), "seconds")
```

上面的代码中，item 为 1 2 3 4 5 的五个任务会一直占用所有的 workers，而 6 7 8 9 10 这五个任务会永远等待！！！

## API 详细说明

concurrent.futures 包含三个部分的 API：
1. PoolExecutor：也就是两个执行器的 API
    - 构造器：主要的参数是 max_workers，用于指定线程池大小（或者说 workers 个数）
    - `submit(fn, *args, **kwargs)`：将任务函数 fn 提交到执行器，args 和 kwargs 就是 fn 需要的参数。
        - 返回一个 future，用于获取结果
    - `map(func, *iterables, timeout=None, chunksize=1)`：当任务是同一个，只有参数不同时，可以用这个方法代替 submit。iterables 的每个元素对应 func 的一组参数。
        - 返回一个 futures 的迭代器
    - `shutdown(wait=True)`：关闭执行器，一般都使用 with 管理器自动关闭。
1. Future：任务被提交给执行器后，会返回一个 future
    - `future.result(timout=None)`：**最常用的方法**，返回任务的结果。如果任务尚未结束，这个方法会一直等待！
        - timeout 指定超时时间，为 None 时没有超时限制。
    - `exception(timeout=None)`：给出任务抛出的异常。和 result() 一样，也会等待任务结束。
    - `cancel()`：取消此任务
    - `add_done_callback(fn)`：future 完成后，会执行 `fn(future)`。
    - `running()`：是否正在运行
    - `done()`：future 是否已经结束了，boolean
    - ...详见官方文档
1. 模块带有的实用函数
    - `concurrent.futures.as_completed(fs, timeout=None)`：等待 fs （futures iterable）中的 future 完成
        - 一旦 fs 中的某 future 完成了，这个函数就立即返回该 future。
        - 这个方法，使每次返回的 future，总是最先完成的 future。而不是先等待任务 1，再等待任务 2...
        - 常通过 `for future in as_completed(fs):` 使用此函数。
    - `concurrent.futures.wait(fs, timeout=None, return_when=ALL_COMPLETED)`：一直等待，直到 return_when 所指定的事发生，或者 timeout
        - return_when 有三个选项：ALL_COMPLETED（fs 中的 futures 全部完成），FIRST__COMPLETED（fs 中任意一个 future 完成）还有 FIRST_EXCEPTION（某任务抛出异常）

## Future 设计模式

这里的 PoolExecutor 的特点，在于它使用了 Future 设计模式，使任务的执行，与结果的获取，变成一个异步的流程。
**我们先通过 submit/map 将任务放入任务队列，这时任务就已经开始执行了！**然后我们在需要的时候，通过 future 获取结果，或者直接 `add_done_callback(fn)`。

这里任务的执行是在新的 workers 中的，主进程/线程不会阻塞，因此主线程可以干其他的事。这种方式被称作异步编程。

## 画外

concurrent.futures 基于 multiprocessing.pool 实现，因此实际上它比直接使用 线程/进程 的 Pool 要慢一点。但是它提供了更方便简洁的 API。

## 参考

- [使用Python进行并发编程-PoolExecutor篇](http://www.dongwm.com/post/78/)
- [Python Parallel Programming Cookbook](https://github.com/laixintao/python-parallel-programming-cookbook-cn)
- [concurrent.futures — Launching parallel tasks](https://docs.python.org/3/library/concurrent.futures.html)
- [进程线程协程与并发并行](https://www.cnblogs.com/kirito-c/p/10306133.html)
- [并行设计模式（一）-- Future模式](https://www.jianshu.com/p/fea4584d2890)