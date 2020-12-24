# Kibana 数据分析

先说一句，对不熟悉 ElasticSearch 的同学而言，刚上手 Kibana 可能会很不适应。
比如搜个关键字结果啥都搜不到，让人怀疑人生。
所以这里先强调一个核心：**ElasticSearch 是以单词为单位进行搜索的！**
如果你搜索某个关键字（比如 `elastic`）啥都搜不到，仔细想想它是不是某个单词的一部分？（`elasticsearch` 的一部分）

而对于中文，在不添加中文分词器的情况下，每个字都被认为是一个「单词」。添加了分词器后，才可以按词进行搜索。

## 一、日志搜索

在使用 EFK 作为 Kubernetes 的日志分析方案时，我们最常使用的，应该就是 Kibana 的「Discover」了，它最大的特点就是：可以使用「Kibana Query Language」在 ES 中快速地查找日志。
下面详细介绍下如何使用 Kibana 查找 K8s 日志。

常见需求：

1. 对某一时段的日志进行聚类，排除掉疯狂重复的日志。

### 零、新建 Pattern、选择时间区间

1. 首先需要新建一个索引匹配的 Pattern，它可以灵活地匹配你想要查询的日志索引。
   1. 建 Pattern 时选择使用 `@timestamp` 为 `Time Filter field name`，方便通过时间进行日志过滤与排序。
   2. 使用 `@timestamp` 有个前提，就是要在 fluentd 中配置收集日志时要带上该字段！
2. 第二步是在「Discover」中选择到对应的时间区间！这样你才能查找到想要的数据。

### 1. [Kibana Query Language](https://www.elastic.co/guide/en/kibana/master/kuery-query.html)

首先介绍下「Kibana Query Language」语法，此语法**在 Kibana 6.x 中需要手动启用！**而在 Kibana 7.x 中已经被设为默认语法。

1. 匹配数字：
    - `response:200`: 匹配所有 response 的值为 200 的 documents
1. 对于数据，可以使用范围操作符：`>` `<` `>=` `<=`
    - `bytes:>1000`: bytes 字段的值要比 1000 大
2. 匹配**单词**：
    - `extension:php` 匹配任何 extension 中包含 `php` 这个单词的 documents
    - 注意 `phphp` 将不会被匹配中！因为这里是按**单词**匹配！
1. 使用通配符 `*`: 如果单词匹配不够用，才考虑使用这个！
    - `response:*`: 任何包含 `response` 属性的 document
    - `machine.os*:"windows 10"`: 通配符也可用于 `key`，匹配任何 `key` 以 `machine.os` 开头，值为 `windows 10` 的 documents
    - `kubernetes.container_name: *service`: 通配符也可以被用在文本的任何部位，比如开头！这里查找所有 service 的 k8s 日志。
2. 默认大小写不敏感
3. 必须使用 `and` `or` 分隔多个搜索术语。比如 `response:200 or extension:php`
4. 加双引号表示不可拆分的整体（即不使用分词器对该文本进行拆解）
    - `message:"Quick brown fox"`: 所有 message 的值包含了 `quick brown fox` 这个词组的 documents
    - 如果不加双引号，ES 会尝试使用分析器对下面这个词组进行拆分，导致搜索时 ES 不会考虑 quick brown fox 的顺序。
5. 使用小括号：
    - `response:(200 or 404)`: 响应为 200 或 400
6. 使用 `not` 进行反匹配
    - `not response:200`: 不是 200 的 documents

#### 使用 KQL 搜索 K8s 日志

搜索所有 `log` 中包含有 XxxError 或 XxxException 的日志：

```
log: (*error or *exception)
```

再限定在所有 xxxworker 日志中进行查找：

```
log: (*error or *exception) and kubernetes.container_name : *worker
```

搜索所有不包含 `info` `debug` 的日志：

```
not log: (debug or info)
```

### 2. 过滤器（Filter）

除了使用 KQL 进行查询，也可以通过添加 Filter 对日志进行过滤。
过滤器会自动生成出对应的 ElasticSearch Query DSL 语句进行查询。

这个比较简单，可以自行尝试。

## 二、数据分析

待续

