# PostgreSQL 插件原理与使用

PostgreSQL 插件（通常称为扩展）是增强数据库功能的重要机制。本章深入探讨 PostgreSQL 插件的工作原理、安装方法和最佳实践。

## 插件工作原理

### 插件架构概述

PostgreSQL 插件系统基于以下几个核心概念：

1. **动态加载**：插件通过动态链接库在运行时加载到 PostgreSQL 服务器进程中
2. **钩子机制**：插件可以通过钩子函数拦截和修改数据库操作
3. **扩展 API**：提供标准化的接口供插件访问数据库内部功能

### 插件加载流程

```sql
-- 1. 插件注册（通过扩展）
CREATE EXTENSION extension_name;

-- 2. 共享库加载
-- PostgreSQL 将加载指定的共享库文件
-- 例如：$libdir/extension_name.so

-- 3. 插件初始化
-- 调用 _PG_init() 函数进行初始化

-- 4. 钩子注册
-- 插件注册各种钩子函数

-- 5. 功能激活
-- 插件开始拦截和处理相应的数据库操作
```

## 核心插件类型

### 1. 认证插件 (Authentication Plugins)

认证插件用于自定义用户认证机制。

```c
// 简单的认证插件示例
#include "postgres.h"
#include "libpq/auth.h"

PG_MODULE_MAGIC;

void
_PG_init(void)
{
    // 注册认证钩子
    ClientAuthentication_hook = my_auth_hook;
}

static void
my_auth_hook(Port *port, int status)
{
    if (status == STATUS_OK)
    {
        // 自定义认证逻辑
        if (check_custom_auth(port))
        {
            // 认证成功
            return;
        }
        else
        {
            // 认证失败
            ereport(FATAL,
                    (errcode(ERRCODE_INVALID_AUTHORIZATION_SPECIFICATION),
                     errmsg("Custom authentication failed")));
        }
    }
}
```

#### 配置认证插件
```bash
# postgresql.conf
shared_preload_libraries = 'my_auth_plugin'

# pg_hba.conf
# local   all             all                                     my_auth_method
```

### 2. 后台工作进程插件 (Background Worker Plugins)

后台工作进程插件允许在数据库中运行自定义的后台任务。

```c
// 后台工作进程插件示例
#include "postgres.h"
#include "access/xlog.h"
#include "postmaster/bgworker.h"
#include "storage/ipc.h"
#include "storage/latch.h"
#include "storage/shmem.h"

PG_MODULE_MAGIC;

static void my_bgworker_main(Datum main_arg);

void
_PG_init(void)
{
    BackgroundWorker worker;

    // 设置工作进程参数
    worker.bgw_flags = BGWORKER_SHMEM_ACCESS | BGWORKER_BACKEND_DATABASE_CONNECTION;
    worker.bgw_start_time = BgWorkerStart_RecoveryFinished;
    worker.bgw_restart_time = BGW_NEVER_RESTART;
    strcpy(worker.bgw_library_name, "my_bgworker");
    strcpy(worker.bgw_function_name, "my_bgworker_main");
    strcpy(worker.bgw_name, "My Background Worker");
    worker.bgw_main_arg = Int32GetDatum(0);

    // 注册后台工作进程
    RegisterBackgroundWorker(&worker);
}

static void
my_bgworker_main(Datum main_arg)
{
    // 连接到数据库
    BackgroundWorkerInitializeConnection("postgres", NULL, 0);

    // 主工作循环
    while (true)
    {
        // 执行后台任务
        // 例如：定期清理、数据聚合等

        // 等待或休眠
        pg_usleep(10000000); // 10秒
    }
}
```

#### 安装和使用后台工作进程
```sql
-- 安装扩展
CREATE EXTENSION my_bgworker;

-- 查看后台工作进程状态
SELECT * FROM pg_stat_activity WHERE backend_type = 'background worker';
```

### 3. 自定义扫描节点插件 (Custom Scan Plugins)

自定义扫描节点插件可以优化特定类型的查询。

```c
// 自定义扫描节点示例
#include "postgres.h"
#include "executor/nodeCustom.h"
#include "nodes/extensible.h"
#include "optimizer/cost.h"

typedef struct MyCustomScanState
{
    CustomScanState css;
    // 自定义状态字段
    List *scan_clauses;
} MyCustomScanState;

// 自定义扫描执行函数
static TupleTableSlot *
MyCustomScanExec(CustomScanState *node)
{
    MyCustomScanState *mycs = (MyCustomScanState *) node;

    // 实现自定义扫描逻辑
    // 例如：使用特定的索引结构或算法

    return NULL; // 返回结果元组
}

// 注册自定义扫描方法
static const CustomExecMethods my_custom_scan_methods = {
    "MyCustomScan",
    BeginCustomScan,
    ExecCustomScan,
    EndCustomScan,
    NULL, // re-initialize
    NULL, // mark pos
    NULL, // restore pos
    NULL  // explain
};

// 创建自定义扫描节点
static Node *
MyCustomCreateCustomScanState(CustomScan *cscan)
{
    MyCustomScanState *mycs = makeNode(MyCustomScanState);

    mycs->css.methods = &my_custom_scan_methods;
    // 初始化自定义状态

    return (Node *) mycs;
}
```

### 4. 统计收集插件

统计收集插件用于收集和分析数据库性能指标。

```c
// 统计收集插件示例
#include "postgres.h"
#include "executor/executor.h"

static ExecutorRun_hook prev_ExecutorRun_hook = NULL;
static void query_stats_hook(QueryDesc *queryDesc, ScanDirection direction, uint64 count, bool execute_once);

void
_PG_init(void)
{
    // 注册执行钩子
    prev_ExecutorRun_hook = ExecutorRun_hook;
    ExecutorRun_hook = query_stats_hook;
}

static void
query_stats_hook(QueryDesc *queryDesc, ScanDirection direction, uint64 count, bool execute_once)
{
    // 收集查询统计信息
    ereport(LOG, (errmsg("Query executed: %s", queryDesc->sourceText)));

    // 调用原始钩子
    if (prev_ExecutorRun_hook)
        prev_ExecutorRun_hook(queryDesc, direction, count, execute_once);
    else
        standard_ExecutorRun(queryDesc, direction, count, execute_once);
}
```

## 常用插件详解

### pg_stat_statements

最常用的查询统计插件，用于跟踪和优化 SQL 查询性能。

```sql
-- 安装和配置
CREATE EXTENSION pg_stat_statements;

-- postgresql.conf 配置
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.max = 10000
pg_stat_statements.track = all
pg_stat_statements.track_utility = off
pg_stat_statements.save = on

-- 重启 PostgreSQL 后使用

-- 查看查询统计
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;

-- 按调用次数排序
SELECT query, calls, total_exec_time
FROM pg_stat_statements
ORDER BY calls DESC
LIMIT 10;

-- 查看特定用户的查询
SELECT query, calls, total_exec_time
FROM pg_stat_statements
WHERE userid = (SELECT oid FROM pg_roles WHERE rolname = 'myuser');

-- 重置统计信息
SELECT pg_stat_statements_reset();

-- 查看查询计划统计
SELECT
    query,
    calls,
    total_plan_time,
    total_exec_time
FROM pg_stat_statements
WHERE calls > 100
ORDER BY (total_plan_time / calls) DESC;
```

### auto_explain

自动记录慢查询的执行计划。

```sql
-- 安装
CREATE EXTENSION auto_explain;

-- postgresql.conf 配置
shared_preload_libraries = 'auto_explain'
auto_explain.log_min_duration = 1000  # 记录超过1秒的查询
auto_explain.log_analyze = true        # 包含执行分析
auto_explain.log_verbose = true        # 详细输出
auto_explain.log_format = json         # JSON 格式
auto_explain.log_timing = true         # 包含时间信息

-- 日志输出示例
-- LOG:  duration: 1234.567 ms  plan:
-- {
--   "Plan": {
--     "Node Type": "Seq Scan",
--     "Relation Name": "users",
--     "Alias": "users",
--     "Startup Cost": 0.00,
--     "Total Cost": 22.50,
--     "Plan Rows": 2250,
--     "Plan Width": 68,
--     "Actual Total Time": 1234.567,
--     "Actual Rows": 5000,
--     "Actual Loops": 1
--   }
-- }
```

### pg_trgm

三元组插件，提供模糊字符串匹配和相似度计算。

```sql
-- 安装
CREATE EXTENSION pg_trgm;

-- 创建测试表
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    content TEXT
);

-- 创建 GIN 索引
CREATE INDEX idx_documents_title_gin ON documents USING GIN (title gin_trgm_ops);
CREATE INDEX idx_documents_content_gin ON documents USING GIN (content gin_trgm_ops);

-- 相似度搜索
SELECT
    id,
    title,
    similarity(title, 'database tutorial') as sim
FROM documents
WHERE title % 'database tutorial'
ORDER BY sim DESC;

-- 自定义相似度阈值
SET pg_trgm.similarity_threshold = 0.6;

-- 模糊匹配
SELECT title FROM documents WHERE title LIKE '%data%';

-- 正则表达式匹配
SELECT title FROM documents WHERE title ~* 'data.*tutorial';

-- 创建扩展索引支持正则表达式
CREATE INDEX idx_documents_title_regex ON documents USING GIN (title gin_trgm_ops);

-- 性能比较
EXPLAIN ANALYZE SELECT * FROM documents WHERE title LIKE '%database%';
EXPLAIN ANALYZE SELECT * FROM documents WHERE title % 'database';
```

### pg_partman

分区管理插件，简化表分区操作。

```sql
-- 安装
CREATE EXTENSION pg_partman;

-- 创建分区表
SELECT partman.run_maintenance_proc();

-- 创建按时间分区的表
SELECT partman.create_parent(
    'public.events',
    'created_at',
    'native',
    'daily'
);

-- 查看分区
SELECT * FROM partman.show_partitions('public.events');

-- 手动创建分区
SELECT partman.run_maintenance_proc();

-- 数据迁移到分区表
INSERT INTO public.events (name, created_at)
SELECT name, created_at FROM old_events;

-- 分区维护
-- 自动创建新分区
SELECT partman.run_maintenance_proc();

-- 删除旧分区
SELECT partman.drop_partition_time(
    'public.events',
    '7 days'
);
```

### pgAudit

审计插件，记录数据库操作日志。

```sql
-- 安装
CREATE EXTENSION pgaudit;

-- postgresql.conf 配置
shared_preload_libraries = 'pgaudit'
pgaudit.log = 'all'              # 记录所有操作
pgaudit.log_catalog = off        # 不记录系统表操作
pgaudit.log_parameter = on       # 记录参数
pgaudit.log_relation = on        # 记录关系操作
pgaudit.log_statement = 'all'    # 记录所有语句
pgaudit.log_level = log          # 日志级别

-- 监控特定用户
ALTER ROLE myuser SET pgaudit.log = 'read, write';
ALTER ROLE myuser SET pgaudit.log_relation = on;

-- 查看审计日志
-- 日志示例：
-- AUDIT: SESSION,1,1,READ,SELECT,TABLE,public.users,SELECT * FROM users WHERE id = 1;

-- 按表过滤
ALTER TABLE sensitive_data SET (pgaudit.log_relation = on);
ALTER TABLE public.data SET (pgaudit.log_relation = off);
```

## 插件开发

### 开发环境设置

```bash
# 安装开发包
sudo apt-get install postgresql-server-dev-all

# 创建插件目录结构
mkdir my_plugin
cd my_plugin

# 创建基本文件
touch my_plugin.c
touch my_plugin.control
touch Makefile
touch my_plugin--1.0.sql
```

### 插件控制文件

```ini
# my_plugin.control
comment = 'My Custom PostgreSQL Plugin'
default_version = '1.0'
module_pathname = '$libdir/my_plugin'
relocatable = true
requires = ''
```

### 插件编译配置

```makefile
# Makefile
MODULE_big = my_plugin
OBJS = my_plugin.o

EXTENSION = my_plugin
DATA = my_plugin--1.0.sql

PG_CONFIG = pg_config
PGXS := $(shell $(PG_CONFIG) --pgxs)
include $(PGXS)
```

### C 插件开发示例

```c
// my_plugin.c
#include "postgres.h"
#include "funcapi.h"
#include "fmgr.h"
#include "utils/builtins.h"

PG_MODULE_MAGIC;

// 示例函数：返回 PostgreSQL 版本
PG_FUNCTION_INFO_V1(get_pg_version);

Datum
get_pg_version(PG_FUNCTION_ARGS)
{
    const char *version = PG_VERSION_STR;
    text *result = cstring_to_text(version);

    PG_RETURN_TEXT_P(result);
}

// 示例函数：计算字符串相似度
PG_FUNCTION_INFO_V1(string_similarity);

Datum
string_similarity(PG_FUNCTION_ARGS)
{
    text *str1 = PG_GETARG_TEXT_P(0);
    text *str2 = PG_GETARG_TEXT_P(1);

    char *cstr1 = text_to_cstring(str1);
    char *cstr2 = text_to_cstring(str2);

    // 简单的相似度算法
    int len1 = strlen(cstr1);
    int len2 = strlen(cstr2);
    float8 similarity = 0.0;

    if (len1 > 0 && len2 > 0)
    {
        int common = 0;
        for (int i = 0; i < len1 && i < len2; i++)
        {
            if (cstr1[i] == cstr2[i])
                common++;
        }
        similarity = (float8)common / (len1 < len2 ? len1 : len2);
    }

    PG_RETURN_FLOAT8(similarity);
}
```

### SQL 安装脚本

```sql
-- my_plugin--1.0.sql

-- 创建函数
CREATE OR REPLACE FUNCTION get_pg_version()
RETURNS TEXT
AS 'MODULE_PATHNAME', 'get_pg_version'
LANGUAGE C STRICT;

CREATE OR REPLACE FUNCTION string_similarity(TEXT, TEXT)
RETURNS DOUBLE PRECISION
AS 'MODULE_PATHNAME', 'string_similarity'
LANGUAGE C STRICT;

-- 示例使用
-- SELECT get_pg_version();
-- SELECT string_similarity('hello', 'hallo');
```

### 插件安装和使用

```bash
# 编译插件
make

# 安装插件
sudo make install

# 在数据库中安装
psql -d mydb -c "CREATE EXTENSION my_plugin;"

# 测试插件功能
psql -d mydb -c "SELECT get_pg_version();"
psql -d mydb -c "SELECT string_similarity('hello', 'hallo');"
```

## 插件管理最佳实践

### 1. 版本管理

```sql
-- 查看插件版本
SELECT * FROM pg_extension WHERE extname = 'pg_stat_statements';

-- 升级插件
ALTER EXTENSION pg_stat_statements UPDATE TO '1.8';

-- 回滚插件版本（需要相应的升级脚本）
ALTER EXTENSION pg_stat_statements UPDATE TO '1.7';
```

### 2. 性能监控

```sql
-- 监控插件性能影响
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'pg_catalog';

-- 查看共享库加载情况
SELECT
    name,
    setting,
    unit,
    short_desc
FROM pg_settings
WHERE name = 'shared_preload_libraries';
```

### 3. 安全配置

```sql
-- 限制插件使用权限
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO myuser;

-- 配置插件特定权限
ALTER ROLE readonly_user SET pgaudit.log = 'none';
ALTER ROLE audit_user SET pgaudit.log = 'all';
```

## 常见问题和故障排除

### 1. 插件加载失败

```bash
# 检查插件文件权限
ls -la $(pg_config --pkglibdir)/my_plugin.so

# 检查日志
tail -f /var/log/postgresql/postgresql-16-main.log

# 检查共享库依赖
ldd $(pg_config --pkglibdir)/my_plugin.so
```

### 2. 内存使用过高

```sql
-- 监控内存使用
SELECT
    datname,
    numbackends,
    xact_commit,
    xact_rollback,
    blks_read,
    blks_hit,
    tup_returned,
    tup_fetched,
    tup_inserted,
    tup_updated,
    tup_deleted
FROM pg_stat_database;
```

### 3. 性能影响

```sql
-- 检查插件对查询性能的影响
EXPLAIN ANALYZE SELECT * FROM large_table WHERE complex_condition;

-- 暂时禁用插件进行对比
SET session_preload_libraries = '';
```

PostgreSQL 插件系统提供了强大的扩展能力，允许开发者根据特定需求定制数据库功能。合理使用插件可以显著提高数据库的功能性和性能，但需要注意插件对系统资源的潜在影响。