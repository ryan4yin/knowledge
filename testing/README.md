# 软件测试

因为软件在使用过程中，遇到的环境非常复杂。
为了测试软件在各种典型环境下的性能，就出现了各种类型的软件测试。

常见的有如下几种：

1. 单元测试(unit-testing)：测试最小单元（比如单个函数/方法），是最贴近代码的测试
1. 集成测试：测试某个由若干单元组成的功能（那不是功能测试？可能理解得不对）。
1. 性能测试(performance-testing)/负载测试(load-testing)：测试软件的性能是否符合要求，或者找出软件的性能上限/瓶颈。
1. API 测试：Web 程序需要
    - 单接口测试
    - 模拟测试：模拟真实用户的请求
    - 全链路测试
1. 时光旅行测试（Time-Travel Testing）：修改系统时间，确认某些和时间有关的逻辑（过期、超时等）正确无误。
    - 这类测试不太好实施，因为修改系统时间可能会导致各种奇怪的问题。
2. 弱网测试：测试软件在网络性能差的情况下的工作状况。
    - 这类测试比较少见。
1. 变异测试(mutation testing): 「变异测试」用于评估测试自身的质量，发现很难意识到的临界情况。

## 相关文档

- [测试的道理](http://www.yinwang.org/blog-cn/2016/09/14/tests)
- [How They Test](https://github.com/abhivaikar/howtheytest): A curated collection of publicly available resources on how software companies around the world test their software systems and build their quality culture.