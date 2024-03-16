### REST

先从 REST 的角度来看看 HTTP 协议规范，

1. URL：需要操作的对象，也就是资源
2. HTTP method：我要对该对象做什么（**POST 增、DELETE 删、GET 查、PUT 和 PATCH 改**）
3. HTTP status code：操作的结果

### HTTP 方法

HTTP 方法有五个值得注意的性质。

1. 前两个属性分别指示该方法的请求和响应是否应该有主体。这个比较重要，因为它涉及到了参数的传递方式。
   比如 GET 方法就不应该含有主体，因此 GET 方法的参数就只能编码在 url 中。
1. 中间三个属性——安全、幂等和可缓存，定义在 [RFC7231](https://tools.ietf.org/html/rfc7231) 中。
   - **安全**：如果一个方法的语义在本质上是「只读」的，那么这个方法就是安全的。客户端向服务端的资源
     发起的请求如果使用了是安全的方法，就不应该引起服务端任何的状态变化，因此也是无害的。此RFC定
     义，GET, HEAD, OPTIONS 和 TRACE 这几个方法是安全的。
   - **幂等**（Idempotent）：幂等的概念是指同一个请求方法执行多次和仅执行一次的效果完全相同。按照RFC
     规范，PUT，DELETE和安全方法都是幂等的。
   - **可缓存**：方法是否可以被缓存。。
1. 该方法是否被表单支持：表单只支持 POST 与 GET

在使用 HTTP 时，我们应当遵循这五个属性。

1. `GET`：请求指定的资源，它的参数用于过滤。使用 `GET` 的请求应该只用于获取数据。

|                         |     |
| ----------------------- | --- |
| 请求是否有主体          | 否  |
| 成功的响应是否有主体    | 是  |
| 安全                    | 是  |
| 幂等                    | 是  |
| 可缓存                  | 是  |
| HTML 表单是否支持该方法 | 是  |

2. `POST`：新增资源。请求主体的类型由 Content-Type 首部指定。 `POST` 不是幂等的，调用多次可能导致新
   增多个资源！

|                         |                |
| ----------------------- | -------------- |
| 请求是否有主体          | 是             |
| 成功的响应是否有主体    | 是             |
| 安全                    | 否             |
| 幂等                    | 否             |
| 可缓存                  | 某些情况下可以 |
| HTML 表单是否支持该方法 | 是             |

3. `PUT`：更换指定的资源。 `PUT` 与 `POST` 方法的区别在于，`PUT` 方法是幂等的，即调用多次与调用一次
   是等价的。

|                         |     |
| ----------------------- | --- |
| 请求是否有主体          | 是  |
| 成功的响应是否有主体    | 否  |
| 安全                    | 否  |
| 幂等                    | 是  |
| 可缓存                  | 否  |
| HTML 表单是否支持该方法 | 否  |

4. `DELETE`：删除指定的资源

|                         |        |
| ----------------------- | ------ |
| 请求是否有主体          | 可以有 |
| 成功的响应是否有主体    | 可以有 |
| 安全                    | 否     |
| 幂等                    | 是     |
| 可缓存                  | 否     |
| HTML 表单是否支持该方法 | 否     |

5. `PATCH`：部分修改指定的资源

|                         |     |
| ----------------------- | --- |
| 请求是否有主体          | 是  |
| 成功的响应是否有主体    | 否  |
| 安全                    | 否  |
| 幂等                    | 否  |
| 可缓存                  | 否  |
| HTML 表单是否支持该方法 | 否  |

REST API 将 url 看作资源，上述五个方法就是对资源的增删查改。

响应码则表示处理结果，可参考 [Github API - v3](https://developer.github.com/v3/) 和
[PayPal API](https://developer.paypal.com/docs/api/overview)

### HTTP 中的数据

#### 请求中的数据

HTTP 请求中，数据可以放在下列几个地方：

1. url 参数：一般只用于添加资源过滤条件。（就像 SQL 的过滤条件一样）
1. cookie：一般只用于保存 session 信息
1. 主体：一般不是表单数据，就是二进制数据。通过 `Content-Type` 指示主体的 MIME 类型。MIME 类型就相当
   于文件的拓展名，在 Web 世界通常都用 MIME 来指示文件的性质和格式。

表单是最常用的数据 POST 方式，也可以考虑使用 json。

#### 表单编码类型

在 html 中，表单的编码方式通过 form 元素的 `enctype`（encode type）指定，

1. 默认是 `application/x-www-form-urlencoded`（requests 也是如此），即表单使用 `urlencode` 编码，然
   后放到主体中。（而不是 url 中）
1. 在表单中包含二进制文件时，就必须手动指定 `enctype="multipart/form-data"`，使用多部分表单编码！否
   则二进制文件不会被传输。
   - 这是因为 `application/x-www-form-urlencoded` 使用 `&` 做参数分隔，它无法编码二进制文件。

而对非表单数据，将 Content-Type 设置为对应的 MIME 类型就行。

#### 响应中的数据

服务器返回数据的手段有：

1. 用 `Set-Cookie` 设置 cookie，而且 `Set-Cookie` 字段可以重复，以设置多个 cookie.
1. 主体，并使用 Content-Type 指示主体类型。

对 REST API 而言，响应最常用的 MIME 应该是 `application/json`.

#### 疑问：响应是否也能用表单形式呢？

首先分析一下如果响应可以用表单，有什么好处：如果需要同时返回二进制和别的参数，一般的方法是使用
base64 编码文件，然后包装成 json 返回，或者将二进制的 URL 放在 json 里。但是用文本编码二进制文件，会
增大数据量，有时一个临时的二进制文件，也不想多此一举再整个 URL。这时如果能够返回类型能使用
`multipart/form-data`，就很方便了。

据我所知，标准的 web 框架没见谁支持这种用法。。。而且就算返回了 `multipart/form-data`，客户端能自动
解析它么？如果能解析，那就很方便。否则可以考虑从服务端 flask 里 copy 一份解析代码出来。。。

> 画外：这种骚操作还是越少用越好。。。

### 补充

其它常用 MIME：

```shell
text/plain
text/html
text/css

image/jpeg
image/png
image/gif
image/svg+xml  # svg

audio/mpeg  # mp3
audio/ogg
audio/*

video/mp4
video/webm

application/*
application/json
application/xml
application/javascript
application/ecmascript
application/octet-stream  # 二进制流

application/pdf
application/zip

application/vnd.ms-excel  # .xls
application/vnd.openxmlformats-officedocument.spreadsheetml.sheet  # .xlsx
application/msword  // .doc
application/vnd.openxmlformats-officedocument.wordprocessingml.document  # .docx
```

### 参考

- [HTTP Methods - MDN](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Methods/POST)
- [get 和 post 的区别？](https://www.zhihu.com/question/28586791)
