# -*- coding: utf-8 -*-
import random
import string
import time
from itertools import chain, zip_longest
from operator import truth

import logging

logger = logging.getLogger(__name__)

"""一些通用的实用函数"""


def group_each(a, size: int, allow_none=False):
    """
        将一个可迭代对象 a 内的元素, 每 size 个分为一组
        group_each([1,2,3,4], 2) -> [(1,2), (3,4)]
    """
    func = zip_longest if allow_none else zip

    iterators = [iter(a)] * size  # 将新构造的 iterator 复制 size 次（浅复制）
    return func(*iterators)  # 然后 zip


def iter_one_by_one(items, allow_none=False):
    func = zip_longest if allow_none else zip

    return chain.from_iterable(func(*items))


def filter_truth(items):
    """过滤掉判断为 False 的 items"""
    return filter(truth, items)


def equal(a, b):
    """判断两个 object 的内容是否一致（只判断浅层数据）"""
    return a.__dict__ == b.__dict__


chars = string.digits + string.ascii_letters
def random_string(length: int, seed: int = None):
    """生成验证码（字符）"""
    if seed:
        random.seed(seed)
    code = "".join(random.choices(chars, k=length))
    return code
