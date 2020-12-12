# dataclass 注意事项

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



