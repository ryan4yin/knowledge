# 拓展 Envoy

扩展 Envoy 的一种方式是实现不同的过滤器，处理或增强请求。这些过滤器可以生成统计数据，翻译协议，修改请求，等等。

另外我们也可以编写实现自己的过滤器，让 Envoy 动态地加载运行它们。

Envoy 支持使用如下几种语言来扩展 Envoy:

- Lua 脚本：Lua 脚本的好处是性能足够高，编写调试方便，甚至可以直接嵌入到 Envoy 配置文件中。
  - Lua 脚本跟 Openresty 一脉相承，是网关/代理领域非常流行的语言
- 原生 C++ API: 这个好处大概是性能好？缺点是比较重。
- WASM: 支持 [proxy-wasm](https://github.com/proxy-wasm) 标准，这是一个代理无关的标准，任何代理都可以实现这个标准。
  - 好处是能同时支持多种静态语言。缺点是目前性能还比较差，而且比较吃内存。
  - 至于可移植性，前景还是挺好的，但是目前的支持仍然比较有限，主要还是 Envoy.
  - 目前比较流行的是 [proxy-wasm-go-sdk](https://github.com/tetratelabs/proxy-wasm-go-sdk) 以及 [proxy-wasm-rust-sdk](https://github.com/proxy-wasm/proxy-wasm-rust-sdk)


一个 Lua 过滤器示例：

```yaml
name: envoy.filters.http.lua
typed_config:
  "@type": type.googleapis.com/envoy.extensions.filters.http.lua.v3.Lua
  # 方法一，直接将脚本嵌入到配置中
  inline_code: |
    -- Called on the request path.
    function envoy_on_request(request_handle)
      -- Do something.
    end
    -- Called on the response path.
    function envoy_on_response(response_handle)
      -- Do something.
    end
#   source_codes:  # 方法二，引用本地的脚本文件
#     myscript.lua:
#       filename: /scripts/myscript.lua
```

Envoy 将上述脚本视为全局脚本，对每一个 HTTP 请求都会分别在请求与响应两个阶段执行其中的两个函数。
