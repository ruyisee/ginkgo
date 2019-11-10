# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-11-10 13:19
"""
import numpy as np


def continuous_change(arr, count, direction=1):
    """
    连续增长或者下跌
    :param arr:  1 - 2 维数据， 二维数据为  （date, symbol)
    :param count: 区间上涨下跌天数
    :param direction: 判断上涨还是下跌
    :return: bool or  bool_list
    """
    pct_change = arr[1:] / arr[:-1]
    if int(direction) == 1:
        mask = np.sum(pct_change > 1, axis=0) >= count
    else:
        mask = np.sum(pct_change < 1, axis=0) >= count
    return mask
