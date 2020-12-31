>个人笔记，如有错误烦请指正。

SQLAlchemy 是一个用 Python 实现的 ORM （Object Relational Mapping）框架，它由多个组件构成，这些组件可以单独使用，也能独立使用。它的组件层次结构如下：

![](https://img2018.cnblogs.com/blog/968138/201901/968138-20190120090336742-1073786018.png)

其中最常用的组件，应该是 **ORM** 和 **SQL 表达式语言**，这两者既可以独立使用，也能结合使用。

**ORM** 的好处在于它
1. 自动处理了数据库和 Python 对象之间的映射关系，屏蔽了两套系统之间的差异。程序员不需要再编写复杂的 SQL 语句，直接操作 Python 对象就行。
1. 屏蔽了各数据库之间的差异，更换底层数据库不需要修改 SQL 语句，改下配置就行。
1. 使数据库结构文档化，models 定义很清晰地描述了数据库的结构。
1. 避免了不规范、冗余、风格不统一的 SQL 语句，可以避免很多人为 Bug，也方便维护。

但是 ORM 需要消耗额外的性能来处理对象关系映射，此外用 ORM 做多表关联查询或复杂 SQL 查询时，效率低下。因此它适用于场景不太复杂，性能要求不太苛刻的场景。

都说 ORM 学习成本高，我自己也更倾向于直接使用 SQL 语句（毕竟更熟悉），因此这一篇笔记不涉及 ORM 部分，只记录 SQLAlchemy 的 Engine 与 SQL 表达式语言。

## 一、直接使用 [Engine](https://docs.sqlalchemy.org/en/latest/core/engines.html#sqlalchemy.create_engine) 和 Connections

第一步是创建数据库引擎实例：

```python
from sqlalchemy import create_engine

engine = create_engine('sqlite:///:memory:', 
                    echo=True,  # echo=True 表示打印出自动生成的 SQL 语句（通过 logging）
                    pool_size=5,  # 连接池容量，默认为 5，生产环境下太小，需要修改。
                    # 下面是 connection 回收的时间限制，默认 -1 不回收
                    pool_recycle=7200)   # 超过 2 小时就重新连接（MySQL 默认的连接最大闲置时间为 8 小时）
```

`create_engine` 接受的第一个参数是数据库 URI，格式为 `dialect+driver://username:password@host:port/database`，dialect 是具体的数据库名称，driver 是驱动名称。key-value 是可选的参数。举例：

```shell
# PostgreSQL
postgresql+psycopg2://scott:tiger@localhost/dbtest

# MySQL + PyMySQL（或者用更快的  mysqlclient）
mysql+pymysql://scott:tiger@localhost/dbtest

# sqlite 内存数据库
# 注意 sqlite 要用三个斜杠，表示不存在 hostname，sqlite://<nohostname>/<path>
sqlite:///:memory:

# sqlite 文件数据库
# 四个斜杠是因为文件的绝对路径以 / 开头：/home/ryan/Codes/Python/dbtest.db
sqlite:////home/ryan/Codes/Python/dbtest.db

# SQL Server + pyodbc
# 首选基于 dsn 的连接，dsn 的配置请搜索hhh
mssql+pyodbc://scott:tiger@some_dsn
```

如果你的密码中含有 '@' 等特殊字符，就不能直接放入 URI 中，必须使用 `urllib.parse.quote_plus` 编码，然后再插入 URI.


引擎创建后，我们就可以直接获取 connection，然后执行 SQL 语句了。这种用法相当于把 SQLAlchemy 当成带 log 的数据库连接池使用：
```python
with engine.connect() as conn:
    res = conn.execute("select username from users")  # 无参直接使用

    # 使用问号作占位符，前提是下层的 DBAPI 支持。更好的方式是使用 text()，这个后面说
    conn.execute("INSERT INTO table (id, value) VALUES (?, ?)", 1, "v1")  # 参数不需要包装成元组

    # 查询返回的是 ResultProxy 对象，有和 dbapi 相同的 fetchone()、fetchall()、first() 等方法，还有一些拓展方法
    for row in result:
        print("username:", row['username'])
```

但是要注意的是，connection 的 execute 是自动提交的（autocommit），这就像在 shell 里打开一个数据库客户端一样，分号结尾的 SQL 会被自动提交。
只有在 `BEGIN TRANSACTION` 内部，`AUTOCOMMIT` 会被临时设置为 `FALSE`，可以通过如下方法开始一个内部事务：
```python
def transaction_a(connection):
    trans = connection.begin()  # 开启一个 transaction
    try:
        # do sthings
        trans.commit()  # 这里需要手动提交
    except:
        trans.rollback()  # 出现异常则 rollback
        raise
# do other things

with engine.connect() as conn:
    transaction_a(conn)
```

### 1. 使用 [text()](https://docs.sqlalchemy.org/en/latest/core/sqlelement.html#sqlalchemy.sql.expression.text) 构建 SQL

相比直接使用 string，text() 的优势在于它：
1. 提供了统一的参数绑定语法，与具体的 DBAPI 无关。
```python
# 1. 参数绑定语法
from sqlalchemy import text

result = connection.execute(
            # 使用 :key 做占位符
            text('select * from table where id < :id and typeName=:type'),
            {'id': 2,'type':'USER_TABLE'})  # 用 dict 传参数，更易读

# 2. 参数类型指定
from sqlalchemy import DateTime

date_param=datetime.today()+timedelta(days=-1*10)
sql="delete from caw_job_alarm_log  where alarm_time < :alarm_time_param"

# bindparams 是 bindparam 的列表，bindparam 则提供参数的一些额外信息（类型、值、限制等）
t=text(sql, bindparams=[bindparam('alarm_time_param', type_=DateTime, required=True)])
connection.execute(t, {"alarm_time_param": date_param})
```

1. 可以很方便地转换 Result 中列的类型
```
stmt = text("SELECT * FROM table",
            # 使用 typemap 指定将 id 列映射为 Integer 类型，name 映射为 String 类型
            typemap={'id': Integer, 'name': String},
          )
result = connection.execute(stmt)
# 对多个查询结果，可以用 for obj in result 遍历
# 也可用 fetchone() 只获取一个
```

## 二、SQL 表达式语言

>复杂的 SQL 查询可以直接用 raw sql 写，而增删改一般都是单表操作，用 SQL 表达式语言最方便。

SQLAlchemy 表达式语言是一个使用 Python 结构表示关系数据库结构和表达式的系统。

### 1. 定义并创建表

SQL 表达式语言使用 Table 来定义表，而表的列则用 Column 定义。Column 总是关联到一个 Table 对象上。

一组 Table 对象以及它们的子对象的集合就被称作「数据库元数据（database metadata）」。metadata 就像你的网页分类收藏夹，相关的 Table 放在一个 metadata 中。

下面是创建元数据（一组相关联的表）的例子，：
```python
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey

metadata = MetaData()  # 先创建元数据（收藏夹）

users = Table('user', metadata,  # 创建 user 表，并放到 metadata 中
              Column('id', Integer, primary_key=True),
              Column('name', String),
              Column('fullname', String)
             )

addresses = Table('address', metadata,
                  Column('id', Integer, primary_key=True),
                  Column('user_id', None, ForeignKey('user.id')),  # 外键约束，引用 user 表的 id 列
                  Column('email_address', String, nullable=False)
                 )

metadata.create_all(engine)  # 使用 engine 创建 metadata 内的所有 Tables（会检测表是否已经存在，所以可以重复调用）
```

#### 表定义中的约束

>应该给所有的约束命名，即为 `name` 参数指定一个不冲突的列名。详见 [The Importance of Naming Constraints](https://alembic.sqlalchemy.org/en/latest/naming.html)

表还有一个属性：[约束条件](https://www.cnblogs.com/kirito-c/p/10295693.html)。下面一一进行说明。

1. **外键约束**：用于在删除或更新某个值或行时，对主键/外键关系中一组数据列强制进行的操作限制。
    1. 用法一：`Column('user_id', None, ForeignKey('user.id'))`，直接在 `Column` 中指定。这也是最常用的方法
    2. 用法二：通过 `ForeignKeyConstraint(columns, refcolumns)` 构建约束，作为参数传给 `Table`.

```python
item = Table('item', metadata,  # 商品 table
    Column('id', Integer, primary_key=True),
    Column('name', String(60), nullable=False),
    Column('invoice_id', Integer, nullable=False),  # 发票 id，是外键
    Column('ref_num', Integer, nullable=False),
    ForeignKeyConstraint(['invoice_id', 'ref_num'],  # 当前表中的外键名称
                         ['invoice.id', 'invoice.ref_num'])  # 被引用的外键名称的序列（被引用的表）
)
```

1. `on delete` 与 `on update`：**外键约束的两个约束条件**，通过 `ForeignKey()` 或 `ForeignKeyConstraint()` 的关键字参数 `ondelete/onupdate` 传入。
可选值有：
    1. **默认行为 `NO ACTION`**：什么都不做，直接报错。
    1. `CASCADE`：删除/更新 父表数据时，**从表数据会同时被 删除/更新**。（无报错）
    1. `RESTRICT`：**不允许直接 删除/更新 父表数据**，直接报错。（和默认行为基本一致）
    1. `SET NULL` or `SET DEFAULT`：删除/更新 父表数据时，将对应的从表数据重置为 `NULL` 或者默认值。
1. **唯一性约束**：`UniqueConstraint('col2', 'col3', name='uix_1')`，作为参数传给 `Table`.
1. **CHECK 约束**：`CheckConstraint('col2 > col3 + 5', name='check1')`， 作为参数传给 `Table`.
1. 主键约束：不解释
    1. 方法一：通过 `Column('id', Integer, primary_key=True)` 指定主键。（参数 `primary_key` 可在多个 `Column` 上使用）
    1. 方法二：使用 `PrimaryKeyConstraint`

```python
from sqlalchemy import PrimaryKeyConstraint

my_table = Table('mytable', metadata,
            Column('id', Integer),
            Column('version_id', Integer),
            Column('data', String(50)),
            PrimaryKeyConstraint('id', 'version_id', name='mytable_pk')
        )
```


### 2. 增删改查语句

1. **增**: 
```python
# 方法一，使用 values 传参
ins = users.insert().values(name="Jack", fullname="Jack Jones")  # 可以通过 str(ins) 查看自动生成的 sql
connection.execute(ins)

# 方法二，参数传递给 execute()
conn.execute(users.insert(), id=2, name='wendy', fullname='Wendy Williams')

# 方法三，批量 INSERT，相当于 executemany
conn.execute(addresses.insert(), [  # 插入到 addresses 表
    {'user_id': 1, 'email_address': 'jack@yahoo.com'},  # 传入 dict 列表
    {'user_id': 1, 'email_address': 'jack@msn.com'},
    {'user_id': 2, 'email_address': 'www@www.org'},
    {'user_id': 2, 'email_address': 'wendy@aol.com'}
])

# 此外，通过使用 bindparam，INSERT 还可以执行更复杂的操作
stmt = users.insert() \ 
         .values(name=bindparam('_name') + " .. name")  # string 拼接
conn.execute(stmt, [
        {'id':4, '_name':'name1'},
        {'id':5, '_name':'name2'},
        {'id':6, '_name':'name3'},
     ])
```

2. **删**：
```python
_table.delete() \
        .where(_table.c.f1==value1) \
        .where(_table.c.f2==value2)  # where 指定条件
```

3. **改**：
```python
# 举例
stmt = users.update() \
             .where(users.c.name == 'jack') \
             .values(name='tom')
conn.execute(stmt)

# 批量更新
stmt = users.update() \
             .where(users.c.name == bindparam('oldname')) \
             .values(name=bindparam('newname'))
conn.execute(stmt, [
     {'oldname':'jack', 'newname':'ed'},
     {'oldname':'wendy', 'newname':'mary'},
     {'oldname':'jim', 'newname':'jake'},
     ])
```

可以看到，所有的条件都是通过 `where` 指定的，它和后面 ORM 的 filter 接受的参数是一样的。（详细的会在第二篇文章里讲）

4. **查**

```python
from sqlalchemy.sql import select

# 1. 字段选择
s1 = select([users])  # 相当于 select * from users
s2 = select([users.c.name, users.c.fullname])  # 这个就是只 select 一部分

# 2. 添加过滤条件
s3 = select([users]) \
    .where(users.c.id == addresses.c.user_id) 

res = conn.execute(s1)
# 可用 for row in res 遍历结果集，也可用 fetchone() 只获取一行
```

查询返回的是 ResultProxy 对象，这是 SQLAlchemy 对 Python DB-API 的 cursor 的一个封装类，要从中获取结果行，主要有下列几个方法：
```python
row1 = result.fetchone()  # 对应 cursor.fetchone()
row2 = result.fetchall()  # 对应 cursor.fetchall()
row3 = result.fetchmany(size=3)  # 对应 cursor.fetchmany(size=3)

row4 = result.first()  # 获取一行，然后立即调用 result 的 close() 方法

col = row[mytable.c.mycol] # 获取 mycol 这一列

result.rowcount  # 结果集的行数

同时，result 也实现了 next protocol，因此可以直接用 for 循环遍历
```

### where 进阶

通过使用 or_、and_、in_ model.join 等方法，where 可以构建更复杂的 SQL 语句。

```python
from sqlalchemy.sql import and_, or_, not_

s = select([(users.c.fullname +
               ", " + addresses.c.email_address).
                label('title')]).\
        where(users.c.id == addresses.c.user_id).\
        where(users.c.name.between('m', 'z')).\
        where(
               or_(
                  addresses.c.email_address.like('%@aol.com'),
                  addresses.c.email_address.like('%@msn.com')
               )
        )
```

## 链接

- [使用 Engines 和 Connections](https://docs.sqlalchemy.org/en/latest/core/connections.html)
- [SQL 表达式语言入门](https://docs.sqlalchemy.org/en/latest/core/tutorial.html)
- [SQLAlchemy - 定义约束](https://docs.sqlalchemy.org/en/13/core/constraints.html)
- [SQLAlchemy个人学习笔记完整汇总](https://www.cnblogs.com/harrychinese/archive/2012/09/12/My_Own_Tutorial_For_SqlAlchemy.html)