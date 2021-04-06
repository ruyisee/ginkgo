# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-11-10 13:19
"""
import numpy as np

from ginkgo import conf


# 去毛票

CN_VOLUME = 1000
CN_PRICE = 1
US_VOLUME = 30000
US_PRICE = 3

POSITION_REVERSE_RATIO = 0.2                                            # 翻转涨跌幅
POSITION_PLATFORM_VOLATILITY = 0.01                                     # 平台波动限制
POSITION_BREAK_RATIO = 0.1                                              # 平台突破最小波动


def moving_average(a, n=3):
    if a.ndim == 2:
        shape = a.shape
        out = np.zeros(shape)

        for i in range(shape[1]):
            out[:, i] = talib.MA(a[:, i], n)

    else:
        out = talib.MA(a, n)
    return out


def extremum(arr):
    """

    :param arr:
    :return: (高点索引， 低点索引）
    """
    max_i = np.argmax(arr)
    min_i = np.argmin(arr)

    if isinstance(max_i, np.ndarray):
        max_i = max_i[-1]
    if isinstance(min_i, np.ndarray):
        min_i = min_i[-1]

    return min_i, max_i


def zigzag_low_corner(corner_index_list, arr, end,
                      down_ext_deviation, ext_backstep, ext_depth):
    pre_direction = 1
    last_high_value = arr[corner_index_list[-1]]
    current_bar_value = arr[end]
    if len(corner_index_list) > 2 and \
            current_bar_value <= arr[corner_index_list[-2]] * down_ext_deviation:
        back_count = 0
        # 区间内新低，back
        while (end - corner_index_list[-2] < ext_depth) and (back_count < ext_backstep):
            corner_index_list.pop()
            corner_index_list.pop()
            if len(corner_index_list) <= 2:
                break
            back_count += 2
            last_high_value = arr[corner_index_list[-1]]
        corner_index_list.append(end)
        pre_direction = -1
    if current_bar_value <= last_high_value * down_ext_deviation:
        # 找到下一个低点
        corner_index_list.append(end)
        pre_direction = -1
    elif current_bar_value >= last_high_value:
        # 新高点，删除上一个高点， 添加新高点
        corner_index_list.pop()
        corner_index_list.append(end)

    return pre_direction, corner_index_list


def zigzag_high_corner(corner_index_list, arr, end,
                       up_ext_deviation, ext_backstep, ext_depth):
    # 下跌方向，寻找下一个高点
    pre_direction = -1
    last_low_value = arr[corner_index_list[-1]]
    current_bar_value = arr[end]
    if len(corner_index_list) > 2 and \
            current_bar_value >= arr[corner_index_list[-2]] * up_ext_deviation:
        # 区间内新高, back
        back_count = 0
        while (end - corner_index_list[-2] < ext_depth) and (back_count < ext_backstep):
            corner_index_list.pop()
            corner_index_list.pop()
            back_count += 2
            if len(corner_index_list) <= 2:
                break
            last_low_value = arr[corner_index_list[-1]]
        corner_index_list.append(end)
        pre_direction = 1
    if current_bar_value >= last_low_value * up_ext_deviation:
        corner_index_list.append(end)
        pre_direction = 1
    elif current_bar_value <= last_low_value:
        # 新低点, 删掉上一个低点， 添加新低点
        corner_index_list.pop()
        corner_index_list.append(end)
    return pre_direction, corner_index_list


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
        if end == ext_depth:  # 第一次计算
            low_i, high_i = extremum(arr[start: end])
            low_i = start + low_i
            high_i = start + high_i
            if low_i < high_i:
                corner_index_list.append(low_i)
                corner_index_list.append(high_i)
                pre_direction = 1  # 高低高
            else:
                corner_index_list.append(high_i)
                corner_index_list.append(low_i)
                pre_direction = -1  # 低高低
        else:  # 后续计算
            if pre_direction <= 0:
                pre_direction, corner_index_list = zigzag_high_corner(corner_index_list,
                                                                      arr,
                                                                      end,
                                                                      up_ext_deviation,
                                                                      ext_backstep,
                                                                      ext_depth)

            else:
                # 上涨方向，寻找下一个低点
                pre_direction, corner_index_list = zigzag_low_corner(corner_index_list,
                                                                     arr,
                                                                     end,
                                                                     down_ext_deviation,
                                                                     ext_backstep,
                                                                     ext_depth)

        # 下次循环index
        start = start + 1
        end = start + ext_depth
        if end >= len(arr):
            break
    return corner_index_list


def remove_cent(close_arr: np.ndarray, volume_arr: np.ndarray, symbols, market='US',
                hk_volume=CN_VOLUME, hk_price=CN_PRICE, us_volume=US_VOLUME, us_price=US_PRICE):
    """
    去掉仙股
    :param close_arr: shape(symbol, ) 的 一维 ndarray 最新股价对象
    :param volume_arr: shape( timestamp, symbol) 的 二维 ndarray 对象
    :param symbols: list-like
    :param market:
    :return: symbols-list-removed-cent
    """
    if len(volume_arr) < 60:
        raise ValueError('length of volume_arr mast be large than 60')
    if len(volume_arr[0]) != len(close_arr[0]) or len(close_arr[0]) != len(symbols):
        raise ValueError('len(volume_arr[0]) == len(close_arr) == len(symbols)')

    volume_arr = volume_arr[-30:]
    close_arr = close_arr[-30:]
    if market == 'US':
        close_mask = close_arr[-1] > us_price
        volume_mask = volume_arr > us_volume
    elif market == 'HK':
        close_mask = close_arr[-1] > hk_price
        volume_mask = volume_arr > hk_volume
    else:
        raise NotImplementedError
    mask = close_mask & (volume_mask.all(axis=0))
    if not isinstance(symbols, np.ndarray):
        symbols = np.array(symbols)
    return symbols[mask].tolist()


def current_position(close_arr, reverse_ratio=POSITION_REVERSE_RATIO, platform_volatility=POSITION_PLATFORM_VOLATILITY,
                     break_ratio=POSITION_BREAK_RATIO):
    """
    :param close_arr: np.array,  (datetime, symbols), 时间方向长度要大于60
    :param reverse_ratio: 翻转率
    :param platform_volatility: 平台波动率最大限制
    :param break_ratio: 平台突破波动率
    :return: np.ndarray(int)
    # 低位翻转 1, 高位翻转 -1
    # 调整突破 2，调整向下突破 -2
    # 多头排列 3， 空头排列-3
    """
    if close_arr.ndim == 1:
        mask = np.zeros(shape=(1,), dtype='int8')
    else:
        mask = np.zeros(shape=(close_arr.shape[-1],), dtype='int8')
    if len(close_arr) < 60:
        raise ValueError('length of volume_arr mast be large than 60')

    EM5 = moving_average(close_arr, 5)
    EM10 = moving_average(close_arr, 10)
    EM20 = moving_average(close_arr, 20)
    EM30 = moving_average(close_arr, 30)
    EM50 = moving_average(close_arr, 50)

    # 低位翻转 1, 高位翻转 -1
    is_low_reverse = close_arr[-1] < EM50[-1] * (1 - reverse_ratio)
    is_high_reverse = close_arr[-1] > EM50[-1] * (1 + reverse_ratio)
    mask[is_low_reverse] = 1
    mask[is_high_reverse] = -1

    # 调整突破 2，调整向下突破 -2
    tmp_a1 = np.maximum(EM30[-1], EM20[-1])
    tmp_a2 = np.maximum(EM10[-1], EM5[-1])
    a = np.maximum(tmp_a1, tmp_a2)
    tmp_a1 = np.minimum(EM30[-1], EM20[-1])
    tmp_a2 = np.minimum(EM10[-1], EM5[-1])
    b = np.minimum(tmp_a1, tmp_a2)
    close_price_divid_a = close_arr[-1] / a
    close_price_divid_b = close_arr[-1] / b
    is_platform_break_up = (a / b < (1 + platform_volatility)) & \
                           (((1 + break_ratio) > close_price_divid_a) & (close_price_divid_a > 1))
    is_platform_break_down = (a / b < (1 + platform_volatility)) & \
                             (((1 - break_ratio) < close_price_divid_b) & (close_price_divid_b < 1))
    mask[is_platform_break_up] = 2
    mask[is_platform_break_down] = -2

    # 多头排列 3， 空头排列-3
    is_multi = (EM10[-1] > EM20[-1]) & (EM20[-1] > EM30[-1])
    is_short = (EM10[-1] < EM20[-1]) & (EM20[-1] < EM30[-1])
    mask[is_multi] = 3
    mask[is_short] = -3

    if close_arr.ndim == 1:
        return mask[0]
    else:
        return mask

