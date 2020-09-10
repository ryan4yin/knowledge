# Linux Shell 基础

目标：能使用 shell 编写 10 行以内的脚本。更长的脚本应该使用 python 编写。

## 1. For 循环

单行 for 循环，有时候很有用：
```shell
# 数字枚举
for i in $(seq 1 5); do echo $i; done  # sh/bash 都支持
for i in {1..5}; do echo $i; done  # sh 不支持此语法


# 文件枚举，可使用 glob 语法进行文件匹配
for f in *; do echo $f; done
for f in /etc/*.py; do echo $f; done

# 使用 find 进行文件枚举
for f in $(find . -name *.py); do echo $f; done
```

单行 for 循环加几个换行就得到多行 for 循环，格式如下：写脚本用得到，不过更建议用 python:

```shell
for i in $(seq 1 5)
do 
  echo $i
done  # sh/bash 都支持
```

if 语句：

```shell
# 单行 if 语句
if [ true ]; then <command>; fi

#  if else
if [ expression ]
then
   Statement(s) to be executed if expression is true
else
   Statement(s) to be executed if expression is not true
fi
```
