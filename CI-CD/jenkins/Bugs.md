# Jenkins 常见 Bug 整理

## 1. Job Build 僵死，无法终止(unstoppable)

Jenkins 有时会出现一类僵死的 Job Build，手动终止它没有任何效果。目前还没找到具体原因。

手动终止方法：

进入「Manage Jenkins」-「Script Console（脚本命令行）」，然后执行如下脚本强制终止该任务：

```groovy
 Jenkins .instance.getItemByFullName("<JobFullName>")
        .getBuildByNumber(<JobNumber>)
        .finish(hudson.model.Result.ABORTED, new java.io.IOException("Aborting build"));
```

参考资料：

- [How to stop an unstoppable zombie job on Jenkins without restarting the server?](https://stackoverflow.com/questions/14456592/how-to-stop-an-unstoppable-zombie-job-on-jenkins-without-restarting-the-server)

## 2. Windows Slave 的日志中文变成乱码

主要原因是 java 的默认编码、Windows 的系统编码、以及 Jenkins Master 的编码不一致，导致编码错乱。

解决方法是**将所有的编码都统一为 UTF-8**：

1. 在「控制面板」「时间与日期」中修改 Windows 的系统编码为 UTF-8
2. 修改 jenkins-agent 目录下的 `jenkins-slave.xml`，`<arguments>` 中添加参数 `-Dfile.encoding=UTF-8`
3. 在「服务」中重启 jenkins-agent 服务
4. Jenkins Master 我们是 Linux 容器运行的，没啥要改的。

编码统一后，问题就解决了。
