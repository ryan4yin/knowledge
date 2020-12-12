# Java

## 安装 OpenJDK

预编译好的 JDK 中，推荐使用 [AdoptOpenJDK](https://adoptopenjdk.net/)

## 设定默认字符集为 UTF-8

方法一：直接传参数给 `java`:

```
java -Dfile.encoding=UTF-8 -jar xxx.jar
```

方法二：设置环境变量：

```shell
export JAVA_TOOL_OPTIONS="-Dfile.encoding=UTF-8"
```



## 参考

- [多种预编译的 OpenJDK 对比](https://stackoverflow.com/questions/52431764/difference-between-openjdk-and-adoptopenjdk)
