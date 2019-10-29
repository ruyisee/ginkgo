
# -*- coding:utf-8 -*-
"""
@author: fsksf

@since: 2019-10-25 20:59

计算经典形态
"""

import numpy as np


class Classical:

    def __init__(self, open_arr, high_arr, low_arr, close_arr, volume_arr):
        """

        :param open_arr: array
                        1. 计算单个股票， 一位数据： shape(datetime_len, )
                        1. 计算多只股票， 二维数据： shape(datetime_len, symbols_len)

                        \ symbols -->>>
                   time   ---------------------------------------------------------------
                       |[[1.75225e+02 1.80800e+02 2.64760e+02 2.80000e-01 1.71000e+00]
                     A | [1.75880e+02 1.83500e+02 2.62260e+02 2.85000e-01 1.72000e+00]
                     | | [1.78250e+02 1.80400e+02 2.61520e+02 2.86000e-01 1.73000e+00]
                     Z | ...
                     | | [2.04400e+02 1.87420e+02 2.93510e+02 3.39000e+00 7.11000e+00]
                       | [2.03060e+02 1.86300e+02 2.93490e+02 3.51000e+00 7.15000e+00]
                       | [2.09880e+02 1.86750e+02 2.94720e+02 3.46000e+00 7.03500e+00]]

        :param high_arr:
        :param low_arr:
        :param close_arr:
        :param volume_arr:
        """
        self._open_arr = open_arr
        self._high_arr = high_arr
        self._low_arr = low_arr
        self._close_arr = close_arr
        self._volume_arr = volume_arr
        self._ndim = 1
        self._shape = None
        self._check_data()

        self._close_growth = None  # 增量
        self._yesterday_close = None

        self._init_data()

    def _check_data(self):
        try:
            if not (self._open_arr.shape == self._high_arr.shape == self._low_arr.shape ==
                    self._close_arr.shape == self._volume_arr.shape):
                raise ValueError('All inputs must be the same shape')
        except AttributeError as e:
            raise ValueError('All inputs must be of type numpy.array')

        self._ndim = self._open_arr.ndim
        if self._ndim > 2:
            raise ValueError('All inputs ndim must be 1 or 2')

    def _init_data(self):

        self._close_growth = np.diff(self._close_arr, 1, 0)

        self._yesterday_close = self._close_arr[:-1]
        self._yesterday_open = self._open_arr[:-1]
        self._today_open = self._open_arr[1:]

        self._close_change_pct = self._close_growth / self._yesterday_close

    def three_red_soldiers(self, open_pos_pct=0.5, high_pct=0.012):
        """
        1、今天昨天前天三日收盘价持续三日走高；
        2、三日涨幅均在5%以内；
        3、开盘价位于前一天实体的上半部分
        4、最高价/收盘价 < 1.012
        """

        is_high_close_pct = (self._high_arr[-3:] / self._close_arr[-3:]) <= 1 + high_pct
        is_pct_change_in_limit = (self._close_change_pct[-3:] < 0.05) & (self._close_change_pct[-3:] > 0)
        is_open_between = (self._today_open[-2:] >= (self._yesterday_close[-2:] * open_pos_pct +
                                                     self._yesterday_open[-2:] * (1 - open_pos_pct))) & \
                          (self._today_open[-2:] <= self._yesterday_close[-2:])
        return is_pct_change_in_limit.all(axis=0) & is_open_between.all(axis=0) & is_high_close_pct.all(axis=0)

    def three_crow(self, open_pos_pct=0.5, low_pct=0.012):

        is_low_close_pct = (self._close_arr[-3:] / self._low_arr[-3:]) <= 1 + low_pct
        is_pct_change_in_limit = (self._close_change_pct[-3:] > -1 * 0.05) & (self._close_change_pct[-3:] < 0)
        is_open_between = (self._today_open[-2:] <= (self._yesterday_open[-2:] * open_pos_pct +
                                                     self._yesterday_close[-2:] * (1 - open_pos_pct))) & \
                          (self._today_open[-2:] >= self._yesterday_close[-2:])
        return is_pct_change_in_limit.all(axis=0) & is_open_between.all(axis=0) & is_low_close_pct.all(axis=0)

    def multi_cannon(self, growth_pct_min=0.03):
        """
        多方炮
        需要四天数据
        """
        is_u_d_u = (self._close_change_pct[-3] > growth_pct_min) & \
                   (self._close_change_pct[-1] > growth_pct_min) & \
                   (self._close_change_pct[-2] < 0)

        # 昨天阴线收盘要大于前天的开盘价
        is_yesterday_great_bf_open = (self._close_arr[-2] > self._open_arr[-3])
        is_great_growth = (self._close_arr[-1] > self._close_arr[-3])
        return is_u_d_u & is_yesterday_great_bf_open & is_great_growth

    def morning_start(self):
        condition_1 = self._close_arr[-3] / self._open_arr[-3] < 0.95
        condition_2 = self._open_arr[-2] < self._close_arr[-3]
        is_yesterday_cross_star = abs(self._open_arr[-2] - self._close_arr[-2]) / self._close_arr[-2] < 0.03
        is_today_growth = self._close_arr[-1] / self._open_arr[-1] > 1.05
        condition_3 = self._close_arr[-1] > self._close_arr[-3]

        return condition_1 & condition_2 & is_yesterday_cross_star & is_today_growth & condition_3

    def duck_head(self, min_period=8, mid_period=18, max_period=55):
        """
        上涨中继， 老鸭头
        :return:
        """
        E1 = self.moving_average(self._close_arr, n=mid_period)
        E2 = self.moving_average(self._close_arr, n=max_period)


        # 1、前8日中满足“E1<1日前的E1”的天数>=6
        is_min_5_growth = np.sum(np.diff(E1[-min_period-1:-1], 1) > 0) >= 6
        # 2、 今天的E1 > 昨天的E1
        is_mid_today_growth = E1[-1] > E1[-2]
        # 3、最近18天中满足“E2>1日前的E2”的天数>=13
        is_mid_13_growth = np.sum(np.diff(E2[-mid_period:], 1) > 0) >= 13
        # 4、 今天的E2>昨天的E2
        condition_4 = E2[-1] > E2[-2]
        f13 = (self._low_arr[-mid_period:] / E2[-mid_period:] - 1) < 0.1
        # 6、最近18日都满足“E1>E2”
        condition_6 = E1[-mid_period:] > E2[-mid_period:]
        condition_7 = self._close_arr[-min_period:] > E2[-min_period:]
        condition_8 = self._close_arr[-1] > E1[-1]
        condition_9 = E1[-1] / E2[-1] < 1.10

        return is_min_5_growth & is_mid_today_growth & \
               is_mid_13_growth & condition_4 & f13.all(axis=0) & condition_6.all(axis=0) & \
               condition_7.all(axis=0) & condition_8 & condition_9

    def rise_wrap_left(self):

        is_yesterday_fall = (self._close_arr[-2] < self._close_arr[-3]) & (self._close_arr[-2] < self._open_arr[-2])
        is_today_rise = (self._close_arr[-1] > self._close_arr[-2]) & (self._close_arr[-1] < self._open_arr[-1])
        is_wrap = self._close_arr[-1] > self._open_arr[-2]

        return is_yesterday_fall & is_today_rise & is_wrap

    def fall_wrap_left(self):

        is_yesterday_fall = (self._close_arr[-2] < self._close_arr[-3]) & (self._close_arr[-2] < self._open_arr[-2])
        is_today_rise = (self._close_arr[-1] > self._close_arr[-2]) & (self._close_arr[-1] > self._open_arr[-1])
        is_wrap = self._close_arr[-1] < self._open_arr[-2]

        return is_yesterday_fall & is_today_rise & is_wrap

    def rise_pregnant_line(self):

        is_yesterday_fall = (self._close_arr[-2] < self._close_arr[-3]) & (self._close_arr[-2] < self._open_arr[-2])
        is_today_rise = (self._close_arr[-1] > self._close_arr[-2]) & (self._close_arr[-1] > self._open_arr[-1])
        is_wrap = (self._close_arr[-1] < self._open_arr[-2]) & (self._open_arr[-1] > self._close_arr[-2])

        return is_yesterday_fall & is_today_rise & is_wrap

    def golden_spider(self):
        pass

    def dead_spider(self):
        pass

    @staticmethod
    def moving_average(a, n=3):
        if a.ndim == 2:
            axis = 1
        else:
            axis = 0
        ret = np.cumsum(a, dtype=float, axis=axis)
        ret[n:] = ret[n:] - ret[:-n]
        return ret[n - 1:] / n
