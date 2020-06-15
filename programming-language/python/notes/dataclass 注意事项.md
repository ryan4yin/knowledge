# dataclass 注意事项

```python3
from dataclasses import dataclass


@dataclass
class DataType1:
    # 实例属性，需要通过 __init__ 初始化
    a: int
    b: str
    c: str = "abc"  # 有默认值的实例属性

    # 实例属性的默认值不能使用 list dict 等可变类型，默认值使用可变类型是非常危险的！
    h: list = [1, 2, 3]  # 会报错！

    # 不带类型注解的是类属性（所有实例公用），不推荐使用！
    d = "class attribute"

    @property
    def tt(self):
        """
        如果实在需要公共属性，推荐改用这种动态初始化的方式。
        每次调用都会实例化新的值，就不用担心实例之间互相影响。
        """
    return ""
```



