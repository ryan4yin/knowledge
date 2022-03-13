# -*- coding: utf-8 -*-
import secrets
import string
from operator import truth

import logging

logger = logging.getLogger(__name__)

"""一些通用的实用函数"""


def iter_one_by_one(items, stop_immediately=False):
    """
    每次顺序从每个 item 中取出一个元素，跳过已经被迭代完毕的 item.
    :param stop_immediately:  如果捕获到 StopIteration（某个 item 的末尾），就立即结束迭代。
    """
    iters = list(map(iter, items))
    while len(iters):
        for i, it in enumerate(iters):
            try:
                yield next(it)
            except StopIteration:
                if stop_immediately:
                    return  # 立即停止迭代
                
                iters.pop(i)  # 跳过已经迭代完毕的 item


def group_each(a, size: int, padding_with_none=False):
    """
        将一个可迭代对象 a 内的元素, 每 size 个分为一组。
        group_each([1,2,3,4], 2) -> [(1,2), (3,4)]

        :param padding_with_none: 如果最后一组不足 size 个，是否用 None 补足
    """
    one_by_one_list = list(iter_one_by_one(a))
    for i in range(0, len(one_by_one_list), 3):
        upbound = i + 3
        if padding_with_none and upbound > len(one_by_one_list):
            yield one_by_one_list[i:upbound] + [None,]*(upbound-len(one_by_one_list))
        else:
            yield one_by_one_list[i:upbound]


def filter_truth(items):
    """过滤掉判断为 False 的 items"""
    return filter(truth, items)


def equal(a, b):
    """判断两个 object 的内容是否一致（只判断浅层数据）"""
    return a.__dict__ == b.__dict__


chars = string.digits + string.ascii_letters
def random_string(length: int):
    """生成随机字符串"""
    # 注意，这里不应该直接使用 random 库！而应该使用 secrets
    # 尤其是 random 库默认使用当前时间作为 seed，攻击者可以直接遍历最近的时间来猜测随机字符串的内容
    code = "".join(secrets.choice(chars) for _ in range(length))
    return code
