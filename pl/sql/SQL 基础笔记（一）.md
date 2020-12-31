>本笔记整理自[《SQL 基础教程》](https://book.douban.com/subject/24841239/)、[《MySQL 必知必会》](https://book.douban.com/subject/3354490/)和网上资料。个人笔记不保证正确。

## 一、基础

SQL，即结构化查询语言，是为访问与操作关系数据库中的数据而设计的语言。

1. 关系数据库以行(row)为单位读写数据
1. SQL 根据功能的不同，可分为三类（其中DML用得最多，增删查改嘛）
    1. DDL(Data Definition Language, 数据定义语言): CREATE/DROP/ALTER
    2. DML(Data Manipulation Language, 数据操作语言): SELECT/INSERT/UPDATE/DELETE
    3. DCL(Data Control Language, 数据控制语言): COMMIT/ROLLBACK/GRANT/REVOKE
1. SQL 语句要以分号结尾。换行在 SQL 中不表示结束，而等同于空格。
1. SQL 不区分**关键字(Keyword)**的大小写，但是描述符就不一定了。
    - 这里有个坑：MySQL 中，数据库和表其实就是数据目录下的目录和文件，因而，**操作系统的敏感性决定数据库名和表名 是否大小写敏感**。这就意味着**数据库名**和**表名**在 Windows 中是大小写不敏感的，而在大多数类型的 Unix/Linux 系统中是大小写敏感的。（注意仅指数据库名和表名）可通过修改配置文件的`lower_case_table_names`属性来统一这一行为。
    - 而**字段名**、**字段内容**都是内部数据，是操作系统无关的。它们的大小写敏感性，由 MySQL 的的校对（COLLATE）规则来控制。该规则体现在 MySQL 的 校对字符集（COLLATION）的后缀上：比如 utf8字符集，`utf8_general_ci`表示不区分大小写，这个是 utf8 字符集默认的校对规则；`utf8_general_cs` 表示区分大小写，`utf8_bin` 表示二进制比较，同样也区分大小写 。
1. SQL 中的字符串和日期需要用单引号引用起来，日期有特定格式`年-月-日`

修改字符集：`set names <字符集名>`
记住在 MySQL 中，utf-8mb4 才是完全的 utf-8字符集。

## 二、DDL

### 1. 数据库的创建和删除
1. 创建数据库
```sql
CREATE DATABASE <数据库名称>;
```
```sql
DROP DATABASE <数据库名称>;
```

### 2. 创建表：

#### 关系表的设计
关系表的设计，要确保把信息分解成多个表，一类信息一个表，各表通过某些常用的，基本不会改变的值（即关系表设计中的关系，也常称为外键）互相关联。尽量不要有冗余数据。

#### 语句：
```sql
CREATE TABLE <表名>
(
    <列名1> <数据类型> <该列所需约束>,
    <列名2> <数据类型> <该列所需约束>,
    <列名3> <数据类型> <该列所需约束>,
    ...
    <该表的约束1>, <该表的约束2>...
);
```
举例：
```sql
CREATE TABLE `persons`
(
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `name` CHAR(20) NOT NULL, 
    PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```
后面的是设置引擎和默认字符集。工作上，表的设计一定要深思熟虑，因为改起来很困难。

#### 字段类型（MySQL）

有四类数据类型：字符串、数字、日期、二进制。它们又根据数据长度的区别，下分为多个类型。

1. 字符串：
![string types](https://images2018.cnblogs.com/blog/968138/201806/968138-20180615170308408-1360197489.png)
2. 数字
![numeric types](https://images2018.cnblogs.com/blog/968138/201806/968138-20180615170501735-1087517507.png)
3. 日期
![date types](https://images2018.cnblogs.com/blog/968138/201806/968138-20180615170610668-439886214.png)
4. 二进制
![binary types](https://images2018.cnblogs.com/blog/968138/201806/968138-20180615170949680-176119067.png)

#### 约束

SQL 约束是除了数据类型之外，对列中数据追加的限定条件。

1. 类型约束：`NOT NULL`、`AUTO_INCREMENT`、`UNSIGNED`（这个只 MySQL 支持）
1. 默认值：`DEFAULT`，举例 `<列名3> VARCHAR(32) NOT NULL DEFAULT "los angeles"`
2. 表约束：`PRIMARY KEY` 主键约束（主键默认 UNIQUE 且 NOT NULL）

此外还有 `FOREIGN KEY` 和 `CHECK` 两个约束语句，在[进阶笔记](https://www.cnblogs.com/kirito-c/p/10295693.html)中介绍。

>P.S. 字段约束也可以写成表约束（比如主键约束），而反过来很可能不行。

### 3. 删除表和更新表定义
1. 删除表（危险操作）
    - 删除整个表：
```sql
DROP TABLE <表名>;
```
    - 只清空表内数据，但留下表：
```sql
TRUNCATE <表名>;  -- 非标准SQL语句，但是大部分DB都支持。（可能不能ROLLBACK）
```

2. 更新表定义（麻烦的操作）
所以所创建表前要仔细想好格式了，更新表定义是不得已才能为之。
添加列定义：
```sql
ALTER TABLE <表名> ADD COLUMN <列名> <数据类型> <该列的约束>;
```
删除列定义：
```sql
ALTER TABLE <表名> DROP COLUMN <列名>;
```

## 三、DML

>万恶之源 NULL

### 1. 查询（重点）
1. 基本语句：
```
SELECT <字段1> AS <别名1>,
     <字段2> AS <别名2>,
     ...
FROM <表名>
WHERE <过滤条件>;
```
2. 可**用 `DISTINCT` 修饰列名**，使查询结果无重。例：`SELECT DISTINCT <列名> FROM <表名>`
1. 过滤条件可使用比较运算(<>、=等)和逻辑运算(AND OR NOT).
1. 过滤条件中，**比较运算会永远忽略 NULL 值**，如果需要对 NULL 值做操作，需要使用 **IS NULL** 或 **IS NOT NULL**（说忽略也许不太准确，NULL 既不为真也不为假，反正少用NULL。。）
1. 包含NULL的四则运算，得到的结果总为NULL

### 2. 聚合与排序（重点）

#### 聚合函数

即对列进行统计分析的函数，主要有五个：
1. COUNT：计算列的行数。（只有`COUNT(*)`会计算NULL行）
2. SUM：求该列之和。
3. AVG：求该列的平均值。
4. MAX/MIN：求该列的 最大/最小 值

NOTE：
1. **聚合函数计算时会排除所有NULL行。只有COUNT(\*)例外，NULL行也会被它计数。**
1. MAX/MIN 几乎适用于所有数据类型的列（对非数值型，以其二进制值来排序），而SUM/AVG只能用于数值类型的列。
1. 聚合函数操作的列，也能用DISTINCT修饰。例：`SELECT COUNT(DISTINCT <列名>) FROM <表名>`
1. 聚合函数只能用于SELECT子句和还没讲的HAVING子句（以及 ORDER BY 子句）中。

#### 分组(GROUP BY)

分组以聚合键为分类标准，将数据分为多个逻辑组，从而能分别对每个组进行聚合运算。（分组是为了分类聚合）

1. 若出现了 GROUP BY 子句，查询结果一定是每一组一行。
1. GROUP BY 会将 NULL 作为一组特定数据，显示为空。

#### 聚合对SELECT子句的限制
首先要理解的是：
1. 聚合函数的操作对象为某一列，而产生的结果只有一个值。
2. GROUP BY 的操作对象为一列或者多列，产生的结果呢，是每一组一个值。

因此为了避免歧义，只要使用了聚合函数或 GROUP BY 二者之一，SELECT 子句就只能包含：
1. 常数
2. 其他聚合函数（该聚合函数的操作对象可以为其他列）
3. 如果使用了 GROUP BY 子句，还能包括该子句所指定的列名。（也就是聚合键）但是**绝不能包含其他的列名**，因为这会有歧义。

此外，还有一个问题是由 SQL 的执行顺序引起的。应该能很容易猜到，**SELECT 语句的执行顺序和书写顺序是不一致的**。
查询应该是从表开始，所以 FROM 语句一定先执行。然后应该要过滤(WHERE)，再是分组(GROUP BY)，最后才是 SELECT 语句。（就已经学到的子句而言，顺序是这样）
因此按理说，**SELECT 语句 定义的别名，是不能在 GROUP BY 里使用的**。（也有些DB支持该用法，但不通用）

#### 对聚合结果进行过滤(HAVING)
从刚刚说过的SQL执行顺序可见，WHERE要比GROUP BY先执行，因此如果想过滤分组后的结果，不能用它。而应该使用 HAVING 子句。
HAVING 子句和 WHERE 子句都是用来过滤的，但是执行顺序的不同也就决定了它们的用途不同。

NOTE：
1. 有时候，会发现某个过滤条件，不论是先执行（就是写在WHERE子句中）还是后执行（写在HAVING中）都没问题，这时候应该将它写在WHERE子句中，这样GROUP BY操作的数据会更少，处理更快。
1. HAVING 子句的元素，也存在和 SELECT 子句同样的限制。不能使用聚合键以外的列名。

#### 排序(ORDER BY)
**ORDER BY 子句在 SELECT 子句之后执行**，因此它能使用 SELECT 子句中定义的别名。（而 GROUP BY 之前已经说过不能用别名了）
格式：
```sql
SELECT <字段1> AS <别名1>,
     <字段2> AS <别名2>,
     ...
FROM <表名>
WHERE <过滤条件1>
GROUP BY <列名1>, <列名2>...
HAVING <过滤条件2>
ORDER BY <列名/别名1>, <列名/别名2>...  ;
```
1. 多排序键/列：指定多排序键时的排序规则为：**优先使用左侧的列，如果该列存在相同值，再接着参考右侧的键，依此类推。**（如果左侧键值不同，右侧的键就不会被使用了）
1. NULL 值的顺序：**排序键中出现了 NULL 值时，这类值会在结果的开头或结尾汇总**，究竟是排在开头还是结尾，并没有特殊规定。
3. ORDER BY 子句只影响结果的先后顺序，因此排序键可以是结果集以外的东西，比如其他的列，或者使用了 GROUP BY 时，还能用聚合函数。

### 3. 数据的增、删、改
#### 插入(INSERT INTO) 也算用的多了
语法：
```sql
INSERT INTO <表名>
    (列名1, 列名2...)
    VALUES (值1, 值2...);
```
或者也可以使用 SELECT 语句来替代 VALUES 子句，达到将 SELECT 到的结果集插入某表的效果。（但是不要用ORDER BY，因为结果是**集**，没有顺序，排序是徒劳无功的）
插入时主键不能重复，否则会报错。（因此如果需要包含重复数据，一般都会定义一个自增的id字段）

#### 删除(DELETE)

清空表（危险操作，而且效率不如 TRUNCATE）：
```sql
DELETE FROM <表名>;
```

条件删除：
```sql
DELETE FROM <表名>
    WHERE <条件>; 
```

因此使用DELETE时，一定要记得带WHERE，不然就好玩了。。

#### 更新(UPDATE)

```sql
UPDATE <表名>
    SET <列名1> = <算术表达式1>,
        <列名2> = <表达式2>,
        ...
    WHERE <条件>;
```
同 DELETE 一样，不带 WHERE 子句的 UPDATE 是很危险的。

## 四、DCL - 事务处理(MySQL)

**事务是一系列不可分割的数据库操作**，也就是说，这一系列操作要么全部执行，要么全部不执行。如果执行过程中发生了问题（检查执行状态），可以通过执行 ROLLBACK 回滚到该事务执行前的状态。（**注意并不会自动回滚**）
```mysql
START TRANSACTION;
    -- do somthing
COMMIT;
```
- `START TRANSACTION`: 标识事务的开始
- `COMMIT`：提交事务。一旦提交，所执行过的操作就已成定论，恢复不了了。
- `ROLLBACK`：事务回滚，**只能回滚未 COMMIT 的 DML 操作！**也就是说只能用在 `START TRANSACTION` 和 `COMMIT` 之间，并且只能回滚 `INSERT/UPDATE/DELETE`。（回滚 SELECT 没啥意义）
- `SAVEPOINT <保留点>` 和 `ROLLBACK TO <保留点>`：同样只能用在 `START TRANSACTION` 和 `COMMIT` 之间，其优势在于，`ROLLBACK TO` 可以指定回滚到某特定保留点，更灵活，而 `ROLLBACK` 只能回滚到事务开始前。

需要注意的有：
1. `COMMIT` 和 `ROLLBACK` 语句也是事务的结束，因此如果执行了 `ROLLBACK`，那它与 `COMMIT` 之间的内容会被跳过。（在这一点上，它相当于大多数 PL 的 return）
1. **如果事务执行出现问题，问题行后面的所有语句都不会被执行！包括 `COMMIT` 和 `ROLLBACK`！** 如果想用纯 SQL 实现事务原子性，必须使用存储过程检查执行状态！举例如下：

```
CREATE PROCEDURE my_test()
    BEGIN
        DECLARE EXIT HANDLER FOR SQLEXCEPTION ROLLBACK  -- 检测到 SQLEXCEPTION 则 rollback，然后 exit
        START TRANSACTION
            INSERT INTO table_test VALUES(1, 'A')
            INSERT INTO table_test VALUES(1, 'B')  -- 这里主键冲突，会触发 SQLEXCEPTION

            COMMIT
    END

CALL my_test()
```
或者**在 PL 中通过异常处理执行 `ROLLBACK`**。（事务虽然中止了，但并未结束！所以仍然可以 `ROLLBACK` 或者 `COMMIT`）

### 数据何时被提交到数据库

1. 显式提交：在事务中使用 `COMMIT` 提交数据操作被称为显式提交
1. 隐式提交：非 DML 操作会被立即提交，也就是说这些语句本身就隐含了提交语义
1. 自动提交： 如果 `AUTOCOMMIT` 被设置为 `ON`，当前 session 中的 DML 语句会在执行后被自动提交（`START TRANSACTION` 内部的 DML 除外，在它内部必须显式 `COMMIT`）

所有的 DML 语句都是要显式提交的，MySQL session 的 `AUTOCOMMIT` 默认为 `ON`，所以 DML 会被自动提交。

>P.S. 许多语言的数据库 API 会定义自己的事务操作，不一定与这里一致。