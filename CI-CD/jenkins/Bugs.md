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


