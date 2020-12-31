>本笔记整理自[《SQL 基础教程》](https://book.douban.com/subject/24841239/)、[《MySQL 必知必会》](https://book.douban.com/subject/3354490/)和网上资料。个人笔记不保证正确。

## 一、复杂查询

### 视图

将 SELECT 查询包装成一个虚拟表，该虚拟表就被称为视图。（因为只是一个包装，因此视图的数据也会随着原表的更新而更新）
1. 用途：
    1. 简化复杂的SQL查询，用它替换子查询，能降低查询的嵌套深度。
    2. SELECT 查询的重用，减少重复查询。
    3. ...
2. 创建视图：
```sql
CREATE VIEW <视图名称>
    (<视图列名1>, <视图列名2>... )
    AS
    <SELECT 语句>;
```
其中 SELECT 的结果列和视图列名一一对应。
3. 视图的限制
    1. 视图的 SELECT 子句，不能包含 ORDER BY 子句。因为视图也是表，而表是集合，它没有顺序。（也有些DB支持该用法，但不通用）
    1. 视图的更新：只在很有限的条件下，才能在视图上使用 INSERT/DELETE/UPDATE 这样的变更数据的语句。（**视图应该只用于检索，能不更新就不要更新它**）
4. 删除视图：`DROP VIEW <视图名称>;`

### 子查询

子查询，其实就是一次性的视图:

```sql
SELECT ...
    FROM (
        SELECT ...  -- 这就是一个子查询：嵌套的 select 语句
    ) AS <别名>
    ...
```
上面的查询的 FROM 子句中，给另一 SELECT 子句定义了一个别名，并将它作为了查询对象。这就是一个子查询。

子查询不仅能用于 FROM，还能用在 WHERE 子句等很多地方。

#### 关联子查询

即用到了外部数据的子查询语句：
```sql
SELECT ...
    FROM product AS p1
    WHERE (
        SELECT ...
            FROM duck AS p2
            WHERE p1.price > p2.price   -- 这里，内部子查询访问了外部查询的表p1，因此是一个关联子查询。
    );
```

## 二、函数、谓词、CASE 表达式

### [**函数**](https://dev.mysql.com/doc/refman/5.7/en/functions.html)
>给出的链接都是 MySQL 的

1. [算术函数](https://dev.mysql.com/doc/refman/5.7/en/numeric-functions.html)
    - 加减乘除：+ - * /
    - ABS 绝对值
    - MOD 求余
    - ROUND 四舍五入
1. [字符串函数](https://dev.mysql.com/doc/refman/5.7/en/string-functions.html)
    - CONCAT(str1,str2,...)   拼接
    - LENGTH(str)  字符串的 **bytes** 长度
    - CHAR_LENGTH(str)
    - LOWER/UPPER  大小写转换
    - REPLACE(str,from_str,to_str) 替换
    -  SUBSTRING(str FROM pos FOR len) 截取
1. [时间和日期函数](https://dev.mysql.com/doc/refman/5.7/en/date-and-time-functions.html)
    - CURRENT_DATE  当前日期
    - CURRENT_TIME 当前时间
    - CURRENT_TIMESTAMP  当前的日期和时间
    - EXTRACT(unit FROM date) 截取日期元素，unit 可为 `YEAR` `MONTH` `HOUR` 等等
1. [转换函数](https://dev.mysql.com/doc/refman/5.7/en/cast-functions.html)
    - CAST(expr AS type) 将 expr 的结果转换成 type 类型
    - [COALESCE(value,...)](https://dev.mysql.com/doc/refman/5.7/en/comparison-operators.html#function_coalesce)  从左往右扫描，返回第一个非 NULL 的值。常用于将 NULL 转换为其他值。eg. COALESCE(sth, 1) 如果 sth 为 NULL 就会返回1.
1. 聚合函数：基本就五个，已经学过了。

### 谓词

即返回布尔值的表达式

#### LIKE谓词——简单字符串匹配（慢）

>匹配整个列

- `%`：任意字符出现任意次
- `_`：匹配任意一个字符

举例：
```sql
SELECT name
    FROM list
    WHERE name LIKE '%Ryan%';  -- 匹配任意包含 'Ryan' 的字符串
```

#### REGEXP谓词——正则字符串匹配

>MySQL 只实现了通用正则的一个子集，而且是search模式。（非match）

#### 其他

- BETWEEN：范围匹配，eg. `BETWEEN 1 AND 10`
- IS NULL、IS NOT NULL
- IN、NOT IN：是否在某集合内
- EXISTS、NOT EXISTS（比较难的一个，入门阶段不要求）：该谓词比较特殊，只需要右侧一个参数，**而且该参数绝大多数情况下，都是一个关联子查询。**而且该子查询的SELECT子句的参数基本可以随意，通常使用`SELECT *`. 对于子查询有返回值的列，它返回True，否则返回False. 但要注意为 NULL 时返回 UNKNOW.（而 WHERE 只认 True）

### CASE 表达式

1. if - else if - else 形式：
```sql
CASE WHEN <求值表达式> THEN <表达式>
    WHEN <求值表达式> THEN <表达式>
    WHEN <求值表达式> THEN <表达式>
    ...
    
    ELSE <表达式>
END
```
2. switch 模式（但不需要break）
```sql
CASE <表达式>
    WHEN <表达式> THEN <表达式>
    WHEN <表达式> THEN <表达式>
    ...
    
    ELSE <表达式>
END
```
这是对 CASE 后的元素做switch比较。

## 三、集合运算

### 注意事项

1. 作为运算对象的结果集，**列字段必须一一对应**，而且对应列的类型必须相同。

### 结果集的交并差

1. `<查询1> UNION <查询2>`：对两个结果集求并
2. `UNION ALL`：添加 ALL 能使结果集包含重复行。
3.  `<查询1> INTERSECT <查询2>`：两结果集的交集
4. `<查询1> EXCEPT <查询2>`：两结果集的差集

### 以列为单位，对表进行联结(JOIN)

>最强大的功能之一



交并差是以行为单位的操作，是竖向的运算。而联结是以列为单位的操作，是横向的拼接。

#### 内联(INNER JOIN)
 
>**内联结果只包含两表的交集**

语法：
```sql
SELECT ...
    FROM (product INNER JOIN shop
        ON product.p_id = shop.p_id)
    WHERE filter_condition;
```
使用 跟在 INNER JOIN 子句后的 ON 子句指定联结条件。（这里我特意用了括号，表示 JOIN 和 ON 两个子句是配套的）

也有另一个很常用的语法（但是现在已经不推荐使用）：
```sql
SELECT ...
    FROM product, shop
    WHERE product.p_id = shop.p_id
        AND filter_condition;
```

对于 shop 表中有多行对应同一个 product 的情况（有多人购买了同一款商品），结果中该 product 会被复制给 shop 中的多个购买记录。（也就是说该 product 会变成多行）

> INNER 可以省略，也就是说只写 JOIN，就默认是 INNER JOIN

#### 外联(OUTER JOIN)

>**外联以某表为主表，将另一表的列联结到该表。**另一表没有值的列，就用 NULL 代替。使用`LEFT` 或 `RIGHT`指定主表。（两个关键字都能实现同样的效果，不过用 LEFT 的多一些）

语法：
```sql
SELECT ...
    FROM product LEFT OUTER JOIN shop
        ON product.p_id = shop.p_id;
```
这和内联很相似，差别只是联结关键词改成了`LEFT OUTER JOIN`。这表示以左边的表为主表，把右边的表的内容联结上去。因此左表的所有列都会出现在结果集中。

多表联查举例：
```sql
-- 登录异常的账号及密码
select distinct batches.identity_number as '登录失败账号', accounts.password
	from ((batches left outer join tasks
			on batches.id = tasks.batch_id)   -- 批次表联结具体的任务表
		left outer join `status`
			on tasks.id = status.task_id)  -- 再联结上状态表
        left outer join accounts
			on batches.identity_number = accounts.identity_number  -- 再联结上账号表
	where `status`.step_type = 'check_login'     -- 只提取 "check_login" 步骤的记录
		and status.status != 'info'  -- 状态不为 info，说明登录异常
```

此外还有 FULL OUTER JOIN 表示返回左右两表的所有行！所有没有匹配的行都给出 NULL

>P.S. 其中的关键字 OUTER 通常可省略。但是 LEFT、RIGHT、FULL 不可以省略。

## 画外：字段引用符号

如果数据库的字段名/数据库名/表名可能和数据库关键字重复，就需要用引用符号将他们引用起来，消除歧义。

MySQL 中经常用反引号干这个事。
而 SQL Server 则使用方括号。
标准 SQL 使用双引号。在看到这些符号时要知道这些差别。

## 查询语句分析

- [MySQL Explain详解](https://www.cnblogs.com/xuanzhi201111/p/4175635.html)

## 常见问题

### 隐式类型转换

在MySQL中，当操作符与不同类型的操作数一起使用时，会发生类型转换以使操作数兼容。则会发生隐式类型转换。

隐式类型转换会导致查询不会走索引！！！可能会严重拖累性能。另外还可能会导致各种奇怪的问题。

详见 [MYSQL隐式类型转换](https://www.cnblogs.com/BOHB-yunying/p/12458589.html)


完。（接下来就是用 Python/Java 连接 MySQL 了）