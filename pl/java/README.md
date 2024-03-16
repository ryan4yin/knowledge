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

## Java 编程相关资料

- [Java 异常处理的误区和经验总结](https://www.ibm.com/developerworks/cn/java/j-lo-exception-misdirection/)
- [从jar包中读取资源文件](https://hxraid.iteye.com/blog/483115)
- [深入解析 Java 反射](https://www.sczyh30.com/posts/Java/java-reflection-1/)

## 参考

- [多种预编译的 OpenJDK 对比](https://stackoverflow.com/questions/52431764/difference-between-openjdk-and-adoptopenjdk)
