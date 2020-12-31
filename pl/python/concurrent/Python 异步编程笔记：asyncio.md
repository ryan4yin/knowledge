>个人笔记，不保证正确。

虽然说看到很多人不看好 asyncio，但是这个东西还是必须学的。。
基于协程的异步，在很多语言中都有，学会了 Python 的，就一通百通。

### 一、生成器 generator

Python 的 asyncio 是通过 generator 实现的，要学习 async，先得复习下 generator.

#### 1. yield

众所周知，yield 是用于定义 generator 函数的关键字，调用该函数，会返回一个 generator

```python
>>> def f():
...     yield 1
...     yield 2
... 
>>> f()  # 返回的是 generator
<generator object f at 0x7f672c460570>
>>> g = f()
>>> next(g)  # 通过 next 方法从 generator 获取值
1
>>> g.__next__()  # next 方法实际是调用了 generator 的 __next__ 方法
2
>>> next(g)  # 生成器运行结束，产生一个 StopIteration 的 exception
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
```
每次调用 next，generator 都只会运行到下一个 yield 关键字所在行，返回 yield 右侧的对象，然后暂停在该处，等待下一次 next 调用。

从上面的例子看，yield 就是延迟求值而已。**但是 yield 还有一个特性，就是它是一个 expression，有返回值！**看例子：

```Python
>>> def func():
...     r = yield 1
...     yield r
... 
>>> g = func()
>>> next(g)
1
>>> next(g)  # 通过 next 调用，yield 的返回值为 None
>>> g2 = func()
>>> next(g2)  # 首先需要通过 next 调用，运行到 yield 语句处
1
>>> g2.send(419)  # 现在用 send 方法，这会将当前所在的 yield 语句的值设置为你 send 的值，也就是 419
419  # 然后 generator 运行到下一个 yield，返回右边的值并暂停
```

generator 有四个实例函数：__next__、send 是刚刚已经介绍了的，此外还有 throw 用于从 yield 所在处抛出 Exception，和 close 用于关闭 Generator。详见 [Generator-iterator methods](https://docs.python.org/3/reference/expressions.html#generator-iterator-methods)

#### 2. yield from <iterable>

可以理解成是 `yield <value> from <iterable>`，每次调用时它都会从 \<iterable\> 中取值，直到遇到 StopIteration。才会从下一个 yield 取值。

```python
>>> def f():
...     yield from [1, 2, 3, 4]  # iterable
...     yield 5
...     yield from range(4, 0, -1)  # iterable
... 
>>> list(f())
[1, 2, 3, 4, 5, 4, 3, 2, 1]
```

当然，`yield from <iterable>` 也是一个 expression，也有值。它的值就是 StopIteration 异常的第一个参数，内置类型的这个值都是 None.
```python
>>> def f():
...     r = yield from [1, 2]
...     yield f"value of yield from is {r}"
... 
>>> list(f())
[1, 2, 'value of yield from is None']
```

当 \<iterable\> 是 generator 时，`yield from` 会直接将函数调用委托给这个子 generator，这里的调用包括了前面说过的 next、send、throw、close 四个函数。
并直接将 sub generator yield 的值 yield 给 caller.

#### 3. yield 和 return 混用会发生什么？

generator 中的 `return value`，语义上等同于 `rasie StopIteration(value)`：
```shell
>>> def f():
...     yield 1
...     return 2
...     yield 3  # 永远不会被执行
... 
>>> g = f()
>>> next(g)
1
>>> next(g)  # return 引发 StopIteration
Traceback (most recent call last):
  File "<input>", line 1, in <module>
StopIteration: 2
>>> next(g)  # 再次调用，StopIteration 变成无参了。
Traceback (most recent call last):
  File "<input>", line 1, in <module>
StopIteration
```
可以看到 return 引发了 StopIteration 异常，而 return 的值则成了该异常的第一个参数。

之前说过 `yield from <sub generator>` 表达式的值，就是该 \<sub generator\> 的 StopIteration 异常的第一个参数，因此：
```shell
>>> def f2():
...     a = yield from f()
...     yield a  # a 是 f() 中 return 的值
...     
>>> list(f2())
[1, 2]
```

>[PEP 479 -- Change StopIteration handling inside generators](https://www.python.org/dev/peps/pep-0479/#background-information) 修改了StopIteration 的行为，该 PEP 使人为 raise 的 StopIteration 引发一个 RuntimeError。
该 PEP 在 Python 3.5 版本添加到 __future__ 中，并在 Python 3.7 成为默认行为。
因此除非你确实想要引发异常，否则应该使用 return 来结束一个 generator 并返回值。

### 二、异步IO、协程与非阻塞 IO

先了解一下 [进程线程协程与并发并行](https://www.cnblogs.com/kirito-c/p/10306133.html) 和 [各种 IO 模型](https://www.cnblogs.com/kirito-c/p/10306234.html)

### 三、asyncio 的简单使用

asyncio 引入了两个新关键字：async 和 await，其中 async 能放在三个地方：
1. async def：用于定义异步函数和异步生成器
    - 不含有 yield 的是 async def 定义的是协程函数（coroutine function），调用该函数返回协程对象（coroutine object），协程对象需要通过 EventLoop 运行。
    - 内部含有 yield 的 async def 定义的是异步生成器函数（asynchronous generator function），调用该函数返回异步生成器（async_generator）
        - 异步生成器只能用在 Coroutine 中
    - async def 中不允许使用 yield from
1. async for：表示 for 迭代的是一个异步生成器，该 for 循环的每一次迭代，都是异步的。
    - 只能用在 async def 的内部
1. async with：表示 with 管理的是一个异步上下文管理器（asynchronous context manager）
    - 该 context manager 的 enter 和 exit 两个步骤是异步的
    - 只能用在 async def 的内部

注意异步 generator、context manager，它的 protocol 都和同步的不同，不能混为一谈。
具体而言，对同步 protocol __xxx__ 函数，它的异步版本为 __axxx__，就是加个 a。 

而 await，就相当于 yield from，差别在于 await 是异步的。还有我们关心的是 await 表达式的值，而 yield from 中我们更关心它向上层 yield 的值。

在 yield from 中，当前生成器调用另一个生成器，当前生成器会挂起，直到另一个生成器返回。

但是在 await 中，当前 Coroutine 挂起时， eventloop 会寻找其他 task 来跑，这就利用上了 IO 漫长的等待时间。

async for 是每次迭代都会 await 一次，如果迭代对象是 IO 操作，这个 IO 等待时间就会被利用上。

async with 也是同样，如果 context 的 enter 和 exit 是 IO 操作，这个 IO 时间就会被 eventloop 用于运行其他 task.

使用 asyncio 时，我们要用 async def 将所有的 IO 操作都定义成异步操作。然后在调用时，都使用 await/async for/async with 来调用。

### Coroutine、Task 和 Future

首先，每个协程对象，都是一个独立的协程单元，协程对象之间可以异步运行。

协程需要放到 EventLoop 内运行，要运行一个协程 a，有三种方法：
1. 通过 asyncio.run(coro) 运行一个协程。
    - 该方法会新建一个 EventLoop
1. 在另一个协程 b 中通过 await 调用 a。当 b 运行时， a 也会被 task 运行。
1. 通过 asyncio.create_task(coro)，将需要运行的协程包装成 task，然后通过 task 相关的方法来异步运行它们。
    -  asyncio.gather(*awaitable_objects): 并发执行所有的 task，阻塞到所有 task 结束。返回一个 result 列表。result 的列表顺序和 future 的顺序一致
    - asyncio.as_completed(aws, *, loop=None, timeout=None)，和 gather 的区别在于，它返回一个异步迭代器，每次迭代都返回最先完成的一个 future.


> concurrent.futures 是进程线程的异步执行，而 asyncio 是基于协程的单线程异步执行

### 参考

- [Python服务器编程 - 从 os.fork 到 asyncio](https://zhuanlan.zhihu.com/p/30056870)
- [从0到1，Python异步编程的演进之路](https://zhuanlan.zhihu.com/p/25228075)
- [怎么掌握 asyncio](https://www.zhihu.com/question/294188439/answer/555273313)
- [Python Async/Await入门指南](https://zhuanlan.zhihu.com/p/27258289)
- [谈谈Python协程技术的演进](https://zhuanlan.zhihu.com/p/30275154)
- [Python Doc - Coroutines](https://docs.python.org/3/reference/compound_stmts.html#coroutines)
- [Python Doc - asyncio](https://docs.python.org/3/library/asyncio.html)
