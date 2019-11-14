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


def extremum(arr):
    """

    :param arr:
    :return: (低点索引， 高点索引）
    """
    max_i = np.argmax(arr)
    min_i = np.argmin(arr)

    if isinstance(max_i, np.ndarray):
        max_i = max_i[-1]
    if isinstance(min_i, np.ndarray):
        min_i = min_i[-1]

    return min_i, max_i


def zigzag(arr, ext_depth=12, ext_deviation=0.05, ext_backstep=3):
    """
    :param arr:
    :param ext_depth: 用于设置高低点是相对与过去多少个Bars而言
    :param ext_deviation: 用于设置重新计算高低点时，与前一高低点的相对点差。
                        本算法仅反向翻转使用了精度，同向持续更新end_index
    :param ext_backstep: 用于设置回退计算的Bars的个数。
    :return:
    """
    up_ext_deviation = 1 + ext_deviation
    down_ext_deviation = 1 - ext_deviation
    corner_index_list = []
    pre_direction = 0
    start = 0
    end = ext_depth
    while True:
        current_bar_value = arr[end]
        if end == ext_depth:      # 第一次计算
            low_i, high_i = extremum(arr[start: end])
            low_i = start + low_i
            high_i = start + high_i
            if low_i < high_i:
                corner_index_list.append(low_i)
                corner_index_list.append(high_i)
                pre_direction = 1     # 高低高
            else:
                corner_index_list.append(high_i)
                corner_index_list.append(low_i)
                pre_direction = -1    # 低高低
        else:                       # 后续计算
            if pre_direction <= 0:
                #下跌方向，寻找下一个高点
                last_low_value = arr[corner_index_list[-1]]
                last_high_value = arr[corner_index_list[-2]]
                if current_bar_value >= last_high_value * up_ext_deviation:
                    # 区间内新高
                    corner_index_list.pop()
                    corner_index_list.pop()
                    corner_index_list.append(end)
                    pre_direction = 1
                elif current_bar_value >= last_low_value * up_ext_deviation:
                    corner_index_list.append(end)
                    pre_direction = 1
                elif current_bar_value <= last_low_value:
                    # 新低点, 删掉上一个低点， 添加新低点
                    corner_index_list.pop()
                    corner_index_list.append(end)

            else:
                #上涨方向，寻找下一个低点
                last_high_value = arr[corner_index_list[-1]]
                last_low_value = arr[corner_index_list[-2]]
                if current_bar_value <= last_low_value * down_ext_deviation:
                    # 区间内新低
                    corner_index_list.pop()
                    corner_index_list.pop()
                    corner_index_list.append(end)
                    pre_direction = -1
                elif current_bar_value <= last_high_value * down_ext_deviation:
                    # 找到下一个低点
                    corner_index_list.append(end)
                    pre_direction = -1
                elif current_bar_value >= last_high_value:
                    # 新高点，删除上一个高点， 添加新高点
                    corner_index_list.pop()
                    corner_index_list.append(end)

        # 下次循环index
        start = start+1
        end = start + ext_depth
        if end >= len(arr):
            break
    return corner_index_list