## 如何在 Linux 中运行多个进程

如果是手动运行，有很多种手段:

- tmux
- nohup

但是我们在一些自动化场景中，经常会遇到需要并行运行多个进程，然后等待两个进程退出的场景。


## Shell

注意 shell 版本感觉问题很多，能不用还是尽量不用。

等待所有进程结束才停止：

```shell
#!/bin/bash

pids=""
RESULT=0

./program1 &
pids="$pids $!"

./program2 &
pids="$pids $!"

# for 循环等待所有进程均结束，并收集它们的状态码
# 注意别使用 `jobs -p`，因为如果任务在运行 `jobs -p` 之前就结束，就会被忽略掉
for pid in $pids; do
    wait $pid || let "RESULT=1"
done

if [ "$RESULT" == "1" ]; then
    exit 1
fi
```

等待任意一个进程结束就立即停止：

```shell
#!/bin/bash

./program1 &
./program2 &

# 等待后台任务的任意一个结束，并立即返回其状态码，结束运行。
# 注意此语法需要 bash4.x
wait -n
```


## Python

如果可以使用 Python，那直接使用如下脚本应该是最简明的方法：

```python
import concurrent.futures
import subprocess

cmd_list = [
    "echo a.sh",
    "echo b.sh",
]

def run_cmd(cmd):
    return subprocess.run(cmd, shell=True)

# 使用 with 在离开此代码块时，自动调用 executor.shutdown(wait=true) 释放 executor 资源
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    futures = [executor.submit(run_cmd, cmd) for cmd in cmd_list]

    for future in concurrent.futures.as_completed(futures):
        # 每当其中一个 future 结束，就会运行到这里检查它的结果。
        # 如果 future 有抛出异常，脚本会抛出异常，导致立即结束所有进程。
        future.result()
```


## 参考

- [How to wait in bash for several subprocesses to finish, and return exit code !=0 when any subprocess ends with code !=0?](https://stackoverflow.com/questions/356100/how-to-wait-in-bash-for-several-subprocesses-to-finish-and-return-exit-code-0)
- [How do you run multiple programs in parallel from a bash script?](https://stackoverflow.com/questions/3004811/how-do-you-run-multiple-programs-in-parallel-from-a-bash-script)
