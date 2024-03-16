# dataclass 与 pydantic

pydantic 和 dataclass 是自 Python 推出类型注解以来，使用最方便的数据类工具。

尤其是 pydantic，不仅完全兼容类型注解，还提供了方便的对象序列化、反序列化功能。不论是用来写数据类，
还是编写配置类，都是绝佳利器。

## dataclass 注意事项

```python
from dataclasses import dataclass


@dataclass
class DataType1:
    # 实例属性，需要通过 __init__ 初始化
    a: int
    b: str
    c: str = "abc"  # 有默认值的实例属性

    # 实例属性的默认值不能使用 list dict 等可变类型，默认值使用可变类型是非常危险的！
    h: list = [1, 2, 3]  # 会报错！

    # 不带类型注解的是类属性（所有实例公用），类属性一定要注意只使用不可变类型！
    d = "class attribute"

    def __post__init__(self):
        """
        如果实在需要公共属性，又不方便将它改成不可变类型，推荐改用这种动态初始化的方式。
        在实例化完成之后再初始化这些属性，就不用担心实例之间互相影响。
        """
    return ""
```

## Python 配置的写法

建议使用 `pydantic.BaseSettings` 编写配置类，示例：

```python
from pathlib import Path
from functools import lru_cache
from typing import Optional, Dict, Tuple, List

from pydantic import BaseSettings, Field, RedisDsn, HttpUrl

class HashableMixin:
    def __hash__(self):
        return hash(
            (type(self),) + tuple(getattr(self, it) for it in self.__fields__.keys())
        )


class AppSettings(BaseSettings, HashableMixin):
    name: str = Field(max_length=32, env="APP_NAME")  # 此属性来自环境变量 APP_NAME
    registry_url: HttpUrl  # 来自环境变量 REGISTRY_URL

    vault_url: HttpUrl
    vault_token: str = Filed(max_length=64)

    # 带默认值
    redis_url: RedisDsn = 'redis://user:pass@localhost:6379/1'

    @property
    @lru_cache
    def vault_client(self):
        return VaultClient(self.vault_url, self.vault_token)

    @property
    @lru_cache
    def redis_password(self):
        """从 vault 中获取到 redis 密码"""
        return self.vault_client.get("/app/redis")['password']
```

`BaseSettings` 在实例化时，会自动从 env 环境变量中加载配置，然后会使用提供的 validation 规则进行参数
验证。而一些动态的配置，可以使用 `property` 来设置，既实现了动态，又使用方便，个人觉得很好用。如果某
些动态配置比较消耗时间，可以使用 `lru_cache` 来缓存它，`lru_cache` 要求对象可 hash，为此请继承
`HashableMixin` 这个类。
