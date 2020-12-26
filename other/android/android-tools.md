# Android 自动化测试相关

使用 airtest 进行 Android 自动化测试：

```python
from pathlib import Path

import shlex
import subprocess
from subprocess import CompletedProcess, TimeoutExpired

from loguru import logger

# 下面的 utils 包在当前 git 仓库内
from uitls import shell

def run_airtest(test_case_path: Path):
    """使用 airtest 进行 UI 测试，同时抓取 flutter 输出的日志
    """
    def _run_airtest():
        try:
            return shell.run_cmd(
                f'python3 -m airtest run "{test_case_path.as_posix()}" --device "Android:///" --log',
                capture_output=True,
                encoding="utf-8",
                timeout=Config.testcase_timeout  # 单位：秒
            )
        except TimeoutExpired as e:
            logger.warning(f"测试命令超时！此次测试失败（当前超时时间：{Config.testcase_timeout}）")
            # 用 -100 表示超时
            return CompletedProcess(args=e.args, returncode=-100, stdout=e.stdout, stderr=e.stderr)

    # 1. 通过 adb logcat 命令，获取 app 输出
    # 清理掉所有日志缓存和日志文件中的数据
    shell.run_cmd("adb logcat --clear --file /mnt/sdcard/log.txt")

    logger.info("后台通过 `adb logcat flutter -s --file /mnt/sdcard/log.txt` 命令抓取 app 日志")
    logcat = subprocess.Popen(
        ["adb", 'logcat', 'flutter', '-s', '--file', "/mnt/sdcard/log.txt"],  # 抓取 flutter app 日志
    )
    # logcat.stdout 是一个阻塞的 stream，试了各种方法都无法以非阻塞模式 read 数据

    # 2. 进行UI测试
    result = _run_airtest()

    # 3. 结束 adb logcat 命令
    logcat.terminate()

    # 读取 app_log
    tmp_log_path = Path("app_log.temp")  # 日志临时存放处
    shell.run_cmd(f"adb pull /mnt/sdcard/log.txt {tmp_log_path.as_posix()}", capture_output=True, check=True)
    app_log = tmp_log_path.read_text(encoding="utf-8")

    # 通过 adb 删除 android 设备的所有照片/截图，失败也没事
    shell.run_cmd(f"adb shell rm -r /mnt/sdcard/Pictures", check=False)

    return {
        "status": {
            0: "success",  # 返回 0 表示成功
            -100: "timeout"  # -100 在前面约定好是超时
        }.get(result.returncode, "failed"),  # 任务状态
        "output": result.stderr,  # 该命令的所有输出均在 stderr 中，stdout 不输出日志
        "app_log": app_log
    }
```
