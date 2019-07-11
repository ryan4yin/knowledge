## DevOps 自动化测试、自动化运维


### 1. 各种实用的小脚本（基础啦）
    1. pathlib.Path: 针对 文件夹/文件 的各种操作
    1. subprocess: 调用命令行，可以方便地控制命令的 input/output/errors 管道
    1. pyinvoke: 第三方库，fabric 的下层依赖，比 subprocess 更方便。
    1. 时间日期相关：
        1. time: 常用于获取当前时间，或者将指定的时间转换成别的格式
            1. time.time(): 当前时间戳（相当于 datetime.datetime.now().timestamp()）
            1. time.gmtime()
            1. time.sleep(secs):  这个应该相当熟悉，休眠


