# 如何编写 APISIX lua 插件

通过编写 APISIX 插件，我们可以在请求的各个阶段，对请求进行处理，定制诸如日志、权限管理、负载均衡、限流等等功能。

## APISIX 插件的执行阶段

APISIX 是基于 OpenResty/Nginx 开发的，它提供了八个 Hook 点，分别对应 Lua 插件的 8 个函数，八个 Hook 的执行顺序如下图所示：

![](_img/flow-plugin-internal.png)

各 Hook 按执行顺序介绍如下：

- 阶段一：init 阶段
  - 功能：加载所有的插件
  - 在每个 worker 启动的时候运行
- 阶段二：check_schema 阶段
  - 功能：加载 etcd 中的配置，并调用插件的 check_schema 函数对配置进行校验
  - 每个 worker 启动时，插件加载完成后，就会立即执行这一步骤。
  - 此步骤与请求无关，只在 worker 启动时，以及配置修改时被执行

- 阶段三：rewrite 阶段
  - 功能：权限认证、请求内容的修改、重定向等
  - proxy_rewrite 插件就在这一步执行，可以修改请求的 URI、Host、Headers。

- 阶段四：access 阶段
  - 功能：限流、切量等
  - 官方建议：只有认证逻辑在 rewrite 阶段里面完成，其他需要在代理到上游之前执行的逻辑都放在 access 阶段完成。

- 阶段五：balancer 阶段
  - 功能：流量的负载均衡
  - 在 balancer_by_lua_block 阶段执行 `apisix.http_balancer_phase()`

- 阶段六：head_filter 阶段与 body_filter 阶段：
  - 功能：可修改 upstream 返回的数据
  - 在 `header_filter_by_lua_block` 与 `body_filter_by_lua_block` 中执行

- 阶段七：log 阶段
  - 功能：收集指标、输出日志
  - 在 log_by_lua_block 中执行 `apisix.http_log_phase()`


## APISIX 插件的结构

APISIX 插件的大概结构如下：

```lua
local core            = require("apisix.core")
local plugin          = require("apisix.plugin")
local plugin_name     = "xxx"  --- 插件名称
local new_tab         = require("table.new")
local ngx             = ngx


local schema = {
    type = "object",
    properties = {},
    additionalProperties = false,
}

--- 定义插件的配置结构
local attr_schema = {
    type = "object",
    properties = {
        timeout = {type = "integer", minimum = 1, default = 3},
        fetch_interval = {type = "integer", minimum = 6, default = 300},
    },
    additionalProperties = false,
}

local _M = {
    version = 0.3,
    priority = 510,  --- 插件优先级，数字越大优先级越高
    name = plugin_name,
    attr_schema = attr_schema,
    schema = schema,
}


function _M.check_schema(conf, schema_type)
    --- 此函数将在 check_schema 接段被执行，用于检查配置的正确性
    return core.schema.check(schema, conf)
end

function _M.init()
    --- 此函数将在 init 接段，此插件被 Load 之后执行
    --- the plugins are loaded and init in `init_worker_by_lua_block`
	--- ...
end


function _M.log(conf, ctx)
    --- 此函数将在 log 阶段被执行
end

return _M
```

可以看到，对前面介绍的每个阶段，都可以定义一个同名的函数，该函数将在对应的阶段被调用。

和阶段二到阶段七（请求有关）对应的函数都接收两个参数：`conf` 和 `ctx`，其中：

- `ctx` 包含请求相关的所有上下文，比如 headers url host args 等等
- `conf` 则包含插件的当前配置，配置的结构在前面由 `attr_schema` 定义


# 参考文档
- [插件开发 - APISIX 文档](https://github.com/apache/apisix/blob/master/docs/zh/latest/plugin-develop.md)

