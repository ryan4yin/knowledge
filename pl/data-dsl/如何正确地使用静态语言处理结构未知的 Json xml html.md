## 前言

我日常使用最多的语言是 Python，对一个 Pythonista 而言，处理 json 是一件很简单的事：

```python
In [1]: import json
In [2]: data_json = '{"email": "xxx@example.com", "phone": "13800000001", "nick_name": "ryan_c"}'
In [3]: data_dict = json.loads(data_json)  # 返回 dict 对象
In [4]: data_dict
Out[4]: {'email': 'xxx@example.com', 'phone': '13800000001', 'nick_name': 'ryan_c'}
In [5]: json.dumps(data_dict)  # 返回 json 字符串
Out[5]: '{"email": "xxx@example.com", "phone": "13800000001", "nick_name": "ryan_c"}'
```

我们写爬虫的时候经常这么干，因为实在是很方便。
写日常小脚本时，很少见 pythonista 使用 class 定义 DTO(data type object)，然后对它进行序列化(Marshal)/反序列化(UnMarshal).

**然而这种方法在静态语言中行不通，而且也是非常不推荐的用法。**这就直接导致使用静态语言处理未知的 json 数据时，会显得非常麻烦，体验远远不如 Python。
这主要是因为静态语言需要在编译期就确定对象的类型！

以 Java 为例，如果我们不定义 DTO，打算将一个 json 解析为一个 Map 对象，那么问题就来了：**Map 的 key 和 value 的类型必须在编译期决定**。
可我们编译时根本还不知道 json 数据长什么样！整个 json 数据的 key/value 都是未知的，嵌套深度也是未知的，它的属性甚至可能是动态的。。。
那这样就话，就只能把 Map 定义成 `Map<Object, Object>`。这样 json 是可以解析了，但是处理过程中你又需要做各种各样的类型转换。。。
而且大量使用 Object 完全抛弃掉了静态语言的好处。

如果查看 Java 的知名 json 解析库 `jackson`，能发现它提供了 `ObjectMapper` 和 `JsonNode` 树模型进行 Json 的"流式解析"，不过用起来可比 Python 麻烦多了。

总之，静态语言需要处理 json 数据与类型的映射关系，导致对未知数据结构的解析变得很复杂。

## 解决方法

### 方法一

大部分时候，我们都可以通过定义 DTO 来解决上述问题。

### 方法二

而在某些情况下，比如做爬虫/数据的清晰过滤时，我们只关心 json/html/xml 中的某些属性，完全不 care 其他数据。
这时可以使用一些数据提取专用的语言提取数据，如 `JSONPath`/`正则`/`css`选择器/`xpath`，所有的主流语言基本都有对应的轮子可用。

### 方法三

如果前两种方法都不能满足你的要求，那就只能选择最后的方法：使用 `Map<Object, Object>`/`JsonNode`(Java)、`map[string]interface{}`(Go)，然后自己去遍历了。

## 参考

- Go 语言：[How to Parse JSON in Golang (With Examples)](https://www.sohamkamani.com/blog/2017/10/18/parsing-json-in-golang/)
- Java 语言：[jackson](https://github.com/FasterXML/jackson)
