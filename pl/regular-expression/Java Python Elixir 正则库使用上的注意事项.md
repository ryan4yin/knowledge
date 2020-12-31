>个人笔记，写得乱。。不过自己看得懂就行了—_—

日常工作中能接触到的正则，分为两大派别，其中 Unix-Like 系统中常用的正则，属于 POSIX “派”（较弱），而各编程语言标准库中的 Re，基本都是 PCRE “派”。（详见 [正则表达式“派别”简述](https://liujiacai.net/blog/2014/12/07/regexp-favors/)）

可虽然说各编程语言基本都属于 PCRE 派，实现上却还是各有特点，一个正则想在各语言间移植，也往往需要一番修改。

今天学 Elixir，就在正则上遇到了问题，百度一番，想想索性就把这些差别总结一遍，防止下次又掉坑里。（包括 Python、Java、Elixir、文本编辑器的正则，有时间把 SQL 的正则也写写。。）

## 一、正则库方法上的差别

### 1.1 模式匹配
1. 文本编辑器的正则**是用来搜索的**，会匹配**整段文本中所有符合该模式的字符串**，可以叫做 `find all`。
1. 而不同的编程语言，又要看方法设计上的理念差别：
    - Python 提供了以下方法
        - match：要求必须从字符串开头开始尝试匹配，相当与使用了 PCRE 的 anchored（锚定）模式。（或者说自动在正则开头添加了`\A`，它在 Python 中表示字符串开头）
        - fullmatch：要求必须匹配整个字符串，相当于在正则的开头添加 `\A`，末尾添加 `\Z`（它在 Python 中表示字符串末尾）.
        - search：从字符串中搜索该模式，找到第一个就返回。
        - findall/finditer：这个就对应 editor 的搜索模式，会返回字符串中所有匹配该模式的子字符串
    - Java：Matcher.matches()，尝试将pattern应用到整个字符串上，相当于 py 的 fullmatch().
    - Elixir，它的 re 只是对 erlang 的一个简单封装。
        - match? ：返回 boolean 值，表示是否匹配成功。和 py/java 不同，这个 match? 感觉更像 py 的 search，不过返回值要换成 boolean.所以如果要匹配整个字符串，`\Axxx\z`还挺常用的。
        - named_captures，类似 py 的 search + groupdict()


### 1.2 分组命名
1. 这方面就 Python 的语法和其他的不同，它使用 `(?P<name>your regex)`来为分组命名，而标准语法需要去掉字符`P`. 在正则中 Python 的分组引用方法有`(?P=name)` `\g<name>` `\1` `\2`，前俩好像都是 Python 独有的。只有 `\1` `\2` 通用。

### 1.3 字符串替换
1. 文本编辑器(Sublime/Jetbrains/VSCode)在替换字符串中，使用 `$1` `$2`... 来表示前面捕获的数字分组（在正则中仍然可用 `\1` `\2`，但是替换字符串中必须用 `$1` `$2`）
1. Python 中，替换函数为`re.sub` `re.subn`（是的，不是叫 replace，而是 substitution 的缩写）。而且使用 `\1` `\2`（是的，和正则中的 backreference 一样）来引用前面捕获的分组。（如果命名了分组，也可使用`\g<name>`，但是带`P`的那个语法就不支持了）

## 二、正则书写上的差别

1. Python 有 raw 字符串，Elixir 也有对应的 sigils，在这种字符串里，正则不需要用一大堆反斜线（slash）来转义，而 Java 就不得不如此。
1. Elixir 的 sigils 引用符有 8 种，Python 的字符串引用符也有两种（单引号和双引号），可以通过灵活地换用它们来进一步避免使用转义符。
1. 匹配 flags 的指定方式：
    - 通用写法：可以在正则开头添加`(?aiLmsux)`来指示开启哪些 flags
    - Elixir：写在引用符的最后，eg. `~r/your regex/s`，`s` 表示 dot matches all。
1. 定位点（开头、结尾）：
这一部分感觉不同工具很不一致，有必要写下来
    - 编辑器：默认是打开了多行模式(multiline)的，也就是说`^`匹配字符串开头或者任意一行的开头：`$`匹配字符串的结尾（若结尾有换行，匹配到换行前面的位置），或者任意一行的结尾。
    - 所有的编程语言：默认都不是多行模式，`^`只匹配字符串开头，`$`只匹配字符串结尾（若结尾有换行，匹配到换行前面的位置）。

**NOTE**：但是这里还有个坑，Elixir、Java、C# 都使用 `\A` 来标识字符串的开头，用 `\Z` 来表示字符串结尾（若结尾有换行，匹配到换行前面的位置，和 `$` 一样），**用`\z`小写z 表示字符串的绝对的结尾。（不论结尾是不是换行），可 Python 偏偏用 `\Z` 来表示绝对结尾，并且 Python 里不存在`\z`这个定位符。**
![](https://images2018.cnblogs.com/blog/968138/201807/968138-20180714231219091-337250835.png)
![](https://images2018.cnblogs.com/blog/968138/201807/968138-20180714231224396-995260364.png)

待续

## 其他需要注意的

1. `.` 默认是匹配除**非换行**外的任何字符。如果需要包括换行，需要开启`dot matchs all` 选项，或者使用大小写匹配符结合（如 `[\s\S]` `[\w\W]` 之类）
1. 所有重复限定符(`*` `+` `?` `{m,n}`)，默认都是**贪婪匹配**，如果需要懒惰匹配，要在后面多加个`?`，变成 `*?` `+?` `{m,n}?`、
1. 如果字符串结尾有换行符，`$` 会匹配换行符前面的位置。（也就是说这时它匹配到的位置不是真正的结尾）**如果一定要匹配到结尾，需要用 `\Z`**（Python 应用大写的Z，而 Elixir C# Java 应用小写z）
    - 或者也可以开启 `dollar_endonly` 选项，该选项开启后，`$`就匹配字符串的绝对结尾。（但是在开了 m 选项时，此选项会被忽略）

- 懒惰匹配：
正则匹配默认都是贪婪模式，懒惰匹配要在`重复限定符`后多加一个`?`，表示匹配尽可能少的字符。比如`.*`要改成`.*?`


## 参考

- [正则表达式30分钟入门教程 - v2.3.5](https://deerchao.net/tutorials/regex/regex.htm)
- [正则表达式“派别”简述](https://liujiacai.net/blog/2014/12/07/regexp-favors/)
- [Regex - an online tool to learn, build, & test Regular Expressions](https://regexr.com)

- [Python - re](https://docs.python.org/3/library/re.html)
- [Java - java.util.regex](https://docs.oracle.com/javase/10/docs/api/java/util/regex/package-summary.html)
- [Elixir - Regex](https://hexdocs.pm/elixir/Regex.html)
- [.NET 正则表达式（也就是 C#）](https://docs.microsoft.com/zh-cn/dotnet/standard/base-types/regular-expressions)