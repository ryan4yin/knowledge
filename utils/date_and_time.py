# -*- coding:utf-8 -*-
import time
import datetime as dt


"""
一. 当前时间的获取
"""
# 1. 获取当前时间的时间戳
time.time()  # 直接调用 c api，快: 1561261476.6541092
time_utcnow = dt.datetime.utcnow()  # 当前的世界标准时间
time_utcnow.timestamp()   # 1561261476.654109

# 2. UTC 世界标准时间
time.gmtime()
#输出为： time.struct_time(tm_year=2019, tm_mon=6, tm_mday=23, 
#                         tm_hour=3, tm_min=49, tm_sec=17,
#                         tm_wday=6, tm_yday=174, tm_isdst=0)
# 这实际上是一个元组



"""
二. 时间日期的运算
"""

dt.date
dt.time
dt.datetime  # date 与 time 的结合体
dt.datetime.combine  # date 和 time 不能用加法联结，而必须显式使用这个函数
dt.timedelta  # 做日期加减法时，需要用到它。（也可进行乘除法）



"""
三. 时间日期的格式化
"""

# time.strftime(fmt[, tuple])  # str fromat time，将日期 tuple 转换成指定格式的字符串
# time.strptime(fmt, str)  # str parse time，按给定的格式将字符串解析成 tuple
# datetime 模块，也拥有同样的两个方法

# 格式化为 iso 标准格式
dt.datetime.utcnow().isoformat()  # '2019-06-23T12:38:10.483528'

# 解析 iso 格式的时间字符串(需要 python 3.7+)
time.fromisoformat()
dt.date.fromisoformat()
dt.fromisoformat()

"""
常用的格式化字符串：
1. '%Y-%m-%d %H:%M:%S': '2019-06-23 12:33:34'
1. ISO 格式的日期格式串：'%Y-%m-%dT%H:%M:%S.%fZ'

注意 %f 只对应六位小数，对9位小数它无能为力。。
"""


## 第三方库

"""
标准库 datetime 有时候不太方便，比如没有提供解析 iso 格式的函数。用标准库时，可能经常需要自定义格式化串。
而 maya 和 arrow 这两个第三方库，提供了更方便的函数来干这些事，用上其中之一，就可以让我们少查许多资料。
"""
