# Kibana 数据分析

## 一、日志搜索

在使用 EFK 作为 Kubernetes 的日志分析方案时，我们最常使用的，应该就是 Kibana 的「Discover」了，它最大的特点就是：可以使用「Kibana Query Language」在 ES 中快速地查找日志。
下面详细介绍下如何使用 Kibana 查找 K8s 日志。

## [Kibana Query Language](https://www.elastic.co/guide/en/kibana/master/kuery-query.html)

首先介绍下「Kibana Query Language」语法，此语法**在 Kibana 6.x 中需要手动启用**！而在 Kibana 7.x 中已经被设为默认语法。

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



## 二、数据分析

待续

