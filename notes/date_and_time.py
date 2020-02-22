
# -*- coding:utf-8 -*-
import time
import datetime as dt


"""
一. 时间的获取
"""
# 1. 获取当前时间的时间戳
time.time()  # 直接调用 c api，因此速度很快:  1582315203.537061
utcnow = dt.datetime.utcnow()  # 当前的世界标准时间: datetime.datetime(2020, 2, 22, 4, 0, 3, 537061)
utcnow.timestamp()   # 将标准时转换成时间戳：datetime =>  1582315203.537061

# 2. UTC 世界标准时间
time.gmtime()
#输出为： time.struct_time(tm_year=2019, tm_mon=6, tm_mday=23, 
#                         tm_hour=3, tm_min=49, tm_sec=17,
#                         tm_wday=6, tm_yday=174, tm_isdst=0)
# 这实际上是一个命名元组

# 3. 构建一个指定的 datetime 实例
time_1997 = dt.datetime(year=1997, month=1, day=1)  # => datetime.datetime(1997, 1, 1, 0, 0)
dt.datetime(year=1997, month=1, day=1, minute=11)  # => datetime.datetime(1997, 1, 1, 0, 11)

"""
二. 时间日期的修改与运算
"""

# 0. 日期的修改（修改年月时分秒）
utcnow.replace(day=11)  # =>  datetime.datetime(2020, 2, 11, 4, 0, 3, 537061)  修改 day
utcnow.replace(hour=11)  # => datetime.datetime(2020, 2, 22, 11, 0, 3, 537061)  修改 hour

# 1. 日期与时间
date_utcnow = utcnow.date()  # => datetime.date(2020, 2, 22)  年月日
time_utcnow = utcnow.time()  # => datetime.time(4, 0, 3, 537061)  时分秒

# 2. 联结时间和日期（date 和 time 不能用加法联结）
dt.datetime.combine(date_utcnow, time_utcnow)  # =>  datetime.datetime(2020, 2, 22, 4, 0, 3, 537061)

# 3. 日期的运算

# 3.1 datetime 之间只能计算时间差（减法），不能进行其他运算
utcnow - time_1997  # => datetime.timedelta(days=8452, seconds=14403, microseconds=537061)

# 3.2 使用 timedelta 进行时间的增减
days_step = dt.timedelta(days=1)  # 注意参数是复数形式
time_1997 + days_step  # => datetime.datetime(1997, 1, 2, 0, 0)
time_1997 - days_step  # => datetime.datetime(1996, 12, 31, 0, 0)

# 3.3 timedelta 之间也可以进行加减法
hours_step = dt.timedelta(hours=1)  # => datetime.timedelta(seconds=3600)
days_step + hours_step  # => datetime.timedelta(days=1, seconds=3600)
days_step - hours_step  # => datetime.timedelta(seconds=82800)
hours_step - days_step  # => datetime.timedelta(days=-1, seconds=3600)

# 3.4 timedelta 还可以按比例增减（与数字进行乘除法）
hours_step * 2  # => datetime.timedelta(seconds=7200)
days_step * -2  # => datetime.timedelta(days=-2)
hours_step * 1.1  # =>  datetime.timedelta(seconds=3960)

"""
三. 时间日期的格式化与解析

常用的格式化字符串：
1. 普通格式 - '%Y-%m-%d %H:%M:%S' => '2020-02-22 04:00:03'
1. ISO 格式 - '%Y-%m-%dT%H:%M:%S.%fZ' => '2020-02-22T04:00:03.537061Z'

注：
- strftime: string formate time
- strptime: string parse time
"""

# 1. 将时间格式化成字符串

# 1.1 将 datetime 格式化为 iso 标准格式
utcnow.isoformat()  # =>  '2020-02-22T04:00:03.537061'
utcnow.strftime('%Y-%m-%dT%H:%M:%S.%fZ')   # => '2020-02-22T04:00:03.537061Z'
utcnow.date().strftime('%Y-%m-%dT%H:%M:%S.%fZ')  # => '2020-02-22T00:00:00.000000Z'

# 1.2 将 time.struct_time 格式化为日期字符串（貌似不支持 iso，可能是精度不够）
time.strftime('%Y-%m-%dT%H:%M:%S', gm)  # => '2020-02-22T04:00:03'

# 1.3 将 datetime 格式化成指定格式
utcnow.strftime('%Y-%m-%d %H:%M:%S')  # => '2020-02-22 04:00:03'

# 2. 解析时间字符串

# 2.1 解析 iso 格式的时间字符串，手动指定格式（注意 %f 只对应六位小数，对9位小数它无能为力。。）
dt.datetime.strptime('2020-02-22T04:00:03.537061Z', '%Y-%m-%dT%H:%M:%S.%fZ')  # => datetime.datetime(2020, 2, 22, 4, 0, 3, 537061)

# 2.2 解析 iso 格式的时间字符串(需要 python 3.7+)
dt.datetime.fromisoformat('2020-02-22T04:00:03.537061')  # => datetime.datetime(2020, 2, 22, 4, 0, 3, 537061)
dt.date.fromisoformat('2020-02-22')  # => datetime.date(2020, 2, 22)
dt.time.fromisoformat("04:00:03.537061")  # =>  datetime.time(4, 0, 3, 537061)

# 2.3 解析指定格式的字符串
dt.datetime.strptime('2020-02-22 04:00:03', '%Y-%m-%d %H:%M:%S')  # => datetime.datetime(2020, 2, 22, 4, 0, 3)

## 第三方库

"""
标准库 datetime 有时候不太方便，比如没有提供解析 iso 格式的函数。用标准库时，可能经常需要自定义格式化串。
而 maya 和 arrow 这两个第三方库，提供了更方便的函数来干这些事，用上其中之一，就可以让我们少查许多资料。
"""
