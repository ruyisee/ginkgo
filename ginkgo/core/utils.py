# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-11-10 13:19
"""
import numpy as np


def continuous_change(arr, count, direction=1):
    pct_change = arr[1:] / arr[:-1]
    if int(direction) == 1:
        mask = np.sum(pct_change > 1, axis=0) >= count
    else:
        mask = np.sum(pct_change < 1, axis=0) >= count
    return mask
