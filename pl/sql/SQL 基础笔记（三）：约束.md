>个人笔记不保证正确。

数据类型是限制我们可以在表里存储什么数据的一种方法。不过，对于许多应用来说， 这种限制实在是太粗糙了。比如，一个包含产品价格的字段应该只接受正数。 但是没有哪种标准数据类型只接受正数。 另外一个问题是你可能需要根据其它字段或者其它行的数据来约束字段数据。比如， 在一个包含产品信息的表中，每个产品编号都应该只有一行。

对于这些问题，SQL 允许你在字段和表上定义约束。约束允许你对数据施加任意控制。 如果用户企图在字段里存储违反约束的数据，那么就会抛出一个错误。 这种情况同时也适用于数值来自默认值的情况。

### 1. 外键 `FOREIGN KEY`

外键约束声明一个字段(或者一组字段)的数值必须匹配另外一个表中出现的数值。 
创建外键约束的前提是，该外键所在的表已经存在，并且外键必须是 UNIQUE 的。（主键默认 UNIQUE 且 NOT NULL）
```sql
CREATE TABLE <表名> (
    <字段名> <类型> PRIMARY KEY,
    <字段名> <类型> REFERENCES <外键所在的表名> (<字段名>),  -- 这创建了一个外键
    ...
);
```

还有另一种语法，它支持以多个字段为外键（**字段约束也可以写成表约束，也就是放在一个独立的行中。而反过来很可能不行**）：
```
CREATE TABLE <表名> (
    <字段名1> <类型> PRIMARY KEY,
    <字段名2> <类型>
    <字段名3> <类型>
    ...
    FOREIGN KEY (<字段名2>,  <字段名3>) REFERENCES <外键所在的表名> (<字段名4>, <字段名5>)
);
```

一个表也可以包含多个外键约束。这个特性用于实现表之间的多对多关系。 比如你有关于产品和订单的表，但现在你想允许一个订单可以包含多种产品 (上面那个结构是不允许这么做的)，你可以使用这样的结构：
```sql
CREATE TABLE products (
    product_no integer PRIMARY KEY,
    name text,
    price numeric
);

CREATE TABLE orders (
    order_id integer PRIMARY KEY,
    shipping_address text,
    ...
);

CREATE TABLE order_items (
    product_no integer REFERENCES products,
    order_id integer REFERENCES orders,
    quantity integer,
    PRIMARY KEY (product_no, order_id)
);
```

外键能通过 `ALTER` 语句添加或删除

### 2. 级联操作 `ON DELETE` 与 `ON UPDATE`

上面说过：外键约束声明一个字段(或者一组字段)的数值必须匹配另外一个表中出现的数值。 

但是以 1. 中最后一个 sql 为例，如果一个订单（order）在创建之后，该订单包含的某个产品（product）被删除了，会发生什么？

这个例子中，订单包含的产品通过外键被记录在 order_items 表中。现在如果你要删除 product 中某个被 order_items 引用了的行，默认情况为 `NO ACTION`，就是直接报错。

这个行为也可以手动指定：
```sql
CREATE TABLE products (
    product_no integer PRIMARY KEY,
    name text,
    price numeric
);

CREATE TABLE orders (
    order_id integer PRIMARY KEY,
    shipping_address text,
    ...
);

CREATE TABLE order_items (
    product_no integer REFERENCES products ON DELETE RESTRICT,  -- 限制，也就是禁止删除被它引用的行
    order_id integer REFERENCES orders ON DELETE CASCADE,    -- 级联，在删除被它引用的行的时候，这一行本身也会被自动删除掉
    quantity integer,
    PRIMARY KEY (product_no, order_id)
);
```

除了 `RESTRICT` 和 `CASCADE` 外，在外键上的动作还有两个选项：`SET NULL` 和 `SET DEFAULT`，顾名思义，就是在被引用的行删除后将外键设置为 `NULL` 或默认值。

`ON UPDATE` 与 `ON DELETE` 的动作是一样的，只是 `CASCADE` 表示同步更新。

### 3. `CHECK` 约束

```sql
CREATE TABLE products (
    product_no integer,
    name text,
    price numeric CHECK (price > 0)
);
```

你还可以给这个约束取一个独立的名字。这样就可以令错误消息更清晰， 并且在你需要修改它的时候引用这个名字。语法是：

```sql
CREATE TABLE products (
    product_no integer,
    name text,
    price numeric CONSTRAINT positive_price CHECK (price > 0)
);
```

稍微复杂一点的例子：
```sql
CREATE TABLE products (
    product_no integer,
    name text,
    price numeric CHECK (price > 0),
    discounted_price numeric,
    CHECK (discounted_price > 0 AND price > discounted_price)
);
```

同样的，可以为 CHECK 命名，令错误信息更清晰：

```sql
CREATE TABLE products (
    product_no integer,
    name text,
    price numeric,
    CHECK (price > 0),
    discounted_price numeric,
    CHECK (discounted_price > 0),
    CONSTRAINT valid_discount CHECK (price > discounted_price)
);
```

要注意的是，**当约束表达式计算结果为真或 NULL 的时候，检查约束会被认为是满足条件的**。 因为大多数表达式在含有 NULL 操作数的时候结果都是 NULL ，所以这些约束不能阻止字段值为 NULL 。要排除掉 NULL，只能使用 `NOT NULL` 约束。（所以就说 NULL 是万恶之源hhh）



### 参考

- [约束](http://www.postgres.cn/docs/9.4/ddl-constraints.html)