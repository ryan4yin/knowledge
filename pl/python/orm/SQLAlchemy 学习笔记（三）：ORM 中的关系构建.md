>个人笔记，不保证正确。

## 关系构建：`ForeignKey` 与 `relationship`

关系构建的重点，在于搞清楚这两个函数的用法。`ForeignKey` 的用法已经在 [SQL表达式语言 - 表定义中的约束](https://www.cnblogs.com/kirito-c/p/10269485.html#%E8%A1%A8%E5%AE%9A%E4%B9%89%E4%B8%AD%E7%9A%84%E7%BA%A6%E6%9D%9F) 讲过了。主要是 `ondelete` 和 `onupdate` 两个参数的用法。

## `relationship`

`relationship` 函数在 ORM 中用于构建表之间的关联关系。与 `ForeignKey` 不同的是，它定义的关系不属于表定义，而是动态计算的。
用它定义出来的属性，相当于 SQL 中的视图。

这个函数有点难用，一是因为它的有几个参数不太好理解，二是因为它的参数非常丰富，让人望而却步。下面通过**一对多**、**多对一**、**多对多**几个场景下 `relationship` 的使用，来一步步熟悉它的用法。

首先初始化：
```python3
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
```

### 一对多

```python3
class Parent(Base):
    __tablename__ = 'parent'
    id = Column(Integer, primary_key=True)

    # 因为 Child 中有 Parent 的 ForeignKey，这边的声明不需要再额外指定什么。
    children = relationship("Child")  # children 的集合，相当于一个视图。

class Child(Base):
    __tablename__ = 'child'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('parent.id'))
```

一个 `Parent` 可以有多个 `Children`，通过 `relationship`，我们就能直接通过 `parent.children` 得到结果，免去繁琐的 query 语句。

#### 反向引用

#### 1. `backref` 与 `back_populates`

那如果我们需要得知 `child` 的 `parent` 对象呢？能不能直接访问 `child.parent`？

为了实现这个功能，SQLAlchemy 提供了 `backref` 和 `back_populates` 两个参数。

两个参数的效果完全一致，区别在于，`backref` 只需要在 `Parent` 类中声明 `children`，`Child.parent` 会被动态创建。

而 `back_populates` 必须在两个类中显式地使用 `back_populates`，更显繁琐。（但是也更清晰？）

先看 `backref` 版：
```python3
class Parent(Base):
    __tablename__ = 'parent'
    id = Column(Integer, primary_key=True)
    children = relationship("Child",
                            backref="parent")  # backref 表示，在 Child 类中动态创建 parent 属性，指向当前类。

# Child 类不需要修改
```

再看 `back_populates` 版：
```python3
class Parent(Base):
    __tablename__ = 'parent'
    id = Column(Integer, primary_key=True)
    children = relationship("Child", back_populates="parent")  # back_populates 

class Child(Base):
    __tablename__ = 'child'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('parent.id'))

    # 这边也必须声明，不能省略！
    parent = relationship("Parent", back_populates="children")  # parent 不是集合，是属性！
```

**NOTE：声明的两个 `relationship` 不需要多余的说明，SQLAlchemy 能自动识别到 `parent.children` 是 collection，`child.parent` 是 attribute.**

#### 2. 反向引用的参数：`sqlalchemy.orm.backref(name, **kwargs)`

使用 `back_populates` 时，我们可以很方便地在两个 `relationship` 函数中指定各种参数：
```python3
class Parent(Base):
    __tablename__ = 'parent'
    id = Column(Integer, primary_key=True)
    children = relationship("Child", back_populates="parent", 
                                        lazy='dynamic')  # 指定 lazy 的值

class Child(Base):
    __tablename__ = 'child'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('parent.id'))
    parent = relationship("Parent", back_populates="children", 
                                      lazy='dynamic')  # 指定 lazy 的值
```


但是如果使用 `backref`，因为我们只有一个 `relationship` 函数，`Child.parent` 是被隐式创建的，我们该如何指定这个属性的参数呢？

答案就是 `backref()` 函数，使用它替代 `backref` 参数的值：
```python3
from sqlalchemy.orm import backref

class Parent(Base):
    __tablename__ = 'parent'
    id = Column(Integer, primary_key=True)
    children = relationship("Child",
                            backref=backref("parent", lazy='dynamic'))  # 使用 backref() 函数，指定 Child.parent 属性的参数

# Child 类不需要修改
```

`backref()` 的参数会被传递给 `relationship()`，因此它俩的参数也完全一致。


### 多对一

A many-to-one is similar to a one-to-many relationship. The difference is that this relationship is looked at from the "many" side.

### 一对一

```python3
class Parent(Base):
    __tablename__ = 'parent'
    id = Column(Integer, primary_key=True)
    child = relationship("Child", 
                                    uselist=False,   # 不使用 collection！这是关键
                                    back_populates="parent")

class Child(Base):
    __tablename__ = 'child'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('parent.id'))

     # 包含 ForeignKey 的类，此属性默认为 attribute，因此不需要 uselist=False
    parent = relationship("Parent", back_populates="child") 
```

### 多对多

```python
# 多对多，必须要使用一个关联表！
association_table = Table('association', Base.metadata,
    Column('left_id', Integer, ForeignKey('left.id')),  # 约定俗成的规矩，左边是 parent
    Column('right_id', Integer, ForeignKey('right.id'))  # 右边是 child
)

class Parent(Base):
    __tablename__ = 'left'
    id = Column(Integer, primary_key=True)
    children = relationship("Child",
                    secondary=association_table)  # 专用参数 secondary，用于指定使用的关联表

class Child(Base):
    __tablename__ = 'right'
    id = Column(Integer, primary_key=True)
```

要添加反向引用时，同样可以使用 `backref` 或 `back_populates`.

#### user2user

如果多对多关系中的两边都是 user，即都是同一个表时，该怎么声明？

例如用户的「关注」与「粉丝」，你是 user，你的粉丝是 user，你关注的账号也是 user。

这个时候，关联表 `association_table` 的两个键都是 `user`，**SQLAlchemy 无法区分主次，需要手动指定**，为此需要使用 `primaryjoin` 和 `secondaryjoin` 两个参数。

```
# 关联表，左侧的 user 正在关注右侧的 user
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),  # 左侧
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))  # 右侧，被关注的 user
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # 我关注的 users
    followed = db.relationship(
        'User',
        secondary=followers,  # 指定多对多关联表
        primaryjoin=(followers.c.follower_id == id),  # 左侧，用于获取「我关注的 users」的 join 条件
        secondaryjoin=(followers.c.followed_id == id),  # 右侧，用于获取「我的粉丝」的 join 条件
        lazy='dynamic',  # 延迟求值，这样才能用 filter_by 等过滤函数
        backref=db.backref('followers', lazy='dynamic'))  # followers 也要延迟求值
```
这里比较绕的，就是容易搞混 `primaryjoin` 和 `secondaryjoin` 两个参数。
1. primaryjoin：（多对多中）用于从子对象查询其父对象的 condition（child.parents），默认只考虑外键。
2. secondaryjoin：（多对多中）用于从父对象查询其所有子对象的 condition（parent.children），同样的，默认情况下只考虑外键。


## ORM 层 的 “delete” cascade vs. FOREIGN KEY 层的 “ON DELETE” cascade

之前有讲过 Table 定义中的级联操作：`ON DELETE` 和 `ON UPDATE`，可以通过 `ForeignKey` 的参数指定为 `CASCADE`.

可 SQLAlchemy 还有一个 `relationship` 生成 SQL 语句时的配置参数 `cascade`，另外 `passive_deletes` 也可以指定为 `cascade`。

有这么多的 cascade，我真的是很懵。这三个 cascade 到底有何差别呢？

外键约束中的 `ON DELETE` 和 `ON UPDATE`，与 ORM 层的 `CASCADE` 在功能上，确实有很多重叠的地方。
但是也有很多不同：
1. 数据库层面的 `ON DELETE` 级联能高效地处理 **many-to-one** 的关联；我们在 `many` 方定义外键，也在这里添加 `ON DELETE` 约束。而在 ORM 层，就**刚好相反**。SQLAlchemy 在 `one` 方处理 `many` 方的删除操作，这意味着它更适合处理 **one-to-many** 的关联。
1. 数据库层面上，不带 `ON DELETE` 的外键常用于防止父数据被删除，而导致子数据成为无法被索引到的垃圾数据。如果要在一个 one-to-many 映射上实现这个行为，SQLAlchemy 将外键设置为 NULL 的默认行为可以通过以下两种方式之一捕获：
    1. 最简单也最常用的方法，当然是将外键定义为 **NOT NULL**. 尝试将该列设为 NULL 会触发 NOT NULL constraint exception.
    1. 另一种更特殊的方法，是将 `passive_deletes` 标志设置为字 `all`. 这会完全禁用 SQLAlchemy 将外键列设置为 NULL 的行为，并且 DELETE 父数据而不会对子数据产生任何影响。这样才能触发数据库层面的 `ON DELETE` 约束，或者其他的触发器。
    1. 数据库层面的 `ON DELETE` 级联 比 ORM 层面的级联更高效。数据库可以同时在多个 relationship 中链接一系列级联操作。
    1. SQLAlchemy 不需要这么复杂，因为我们通过将 passive_deletes 选项与正确配置的外键约束结合使用，提供与数据库的 `ON DELETE` 功能的平滑集成。


### 方法一：ORM 层的 cascade 实现

`relationship` 的 `cascade` 参数决定了修改父表时，什么时候子表要进行级联操作。它的可选项有（str，选项之间用逗号分隔）：
1. `save-update`：默认选项之一。在 add（对应 SQL 的 insert 或 update）一个对象的时候，会 add 所有它相关联的对象。
1. `merge`：默认选项之一。在 merge（相当字典的update操作，有就替换掉，没有就合并）一个对象的时候，会 merge 所有和它相关联的对象。
1. `expunge` ：移除操作的时候，会将相关联的对象也进行移除。这个操作只是从session中移除，并不会真正的从数据库中删除。
1. `delete`：删除父表数据时，同时删除与它关联的数据。
1. `delete-orphan`：当子对象与父对象解除关系时，删除掉此子对象（孤儿）。（其实还是没懂。。）
1. `refresh-expire`：不常用。
1. `all`：表示选中除 `delete-orphan` 之外的所有选项。（因此 `all, delete-orphan` 很常用，它才是真正的 `all`）

默认属性是 "save-update, merge".

这只是简略的说明，上述几个参数的详细文档见 [SQLAlchemy - Cascades](https://docs.sqlalchemy.org/en/13/orm/cascades.html#unitofwork-cascades)

### 方法二：数据库层的 cascade 实现

1. 将 `ForeignKey` 的 `ondelete` 和 `onupdate` 参数指定为 `CASCADE`，实现数据库层面的级联。
1. 为 `relationship` 添加关键字参数 `passive_deletes="all"`，这样就完全禁用 SQLAlchemy 将外键列设置为 NULL 的行为，并且 DELETE 父数据不会对子数据产生任何影响。

这样 DELETE 操作时，就会触发数据库的 `ON DELETE` 约束，从而级联删除子数据。


## 参考

- [SQLAlchemy - Relationship Configuration](https://docs.sqlalchemy.org/en/13/orm/relationships.html)
- [SQLAlchemy - Cascades](https://docs.sqlalchemy.org/en/13/orm/cascades.html#unitofwork-cascades)
- [SQLAlchemy 中的 backref 和 back_populates](https://ia.jifangcheng.com/p/46)
- [The Flask Mega-Tutorial Part VIII: Followers](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-viii-followers)