# Python 相关

镜像源设置：

```
# 北外源
pip config set global.index-url https://mirrors.bfsu.edu.cn/pypi/web/simple
```


## 问题定位

在遇到各种隐晦难以定位的问题时，可以使用 `trace` 模块进行调试追踪：

- https://docs.python.org/zh-cn/3.10/library/trace.html
  - 示例：`python3 -m trace --trace -c -g xxx.py > trace.log`
