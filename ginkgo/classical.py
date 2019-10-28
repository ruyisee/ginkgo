
# -*- coding:utf-8 -*-
"""
@author: kangyuqiang

@since: 2019-10-25 20:59
"""

import numpy as np


class Classical:

    def __init__(self, open_arr, high_arr, low_arr, close_arr, volume_arr):
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

        self._close_growth = np.diff(self._close_arr, 1)
        if self._ndim == 2:
            self._yesterday_close = self._close_arr[:, :-1]
            self._yesterday_open = self._open_arr[:, :-1]
            self._today_open = self._open_arr[:, 1:]

        else:
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
        # 上影线小于 20%
        if self._ndim == 1:
            is_high_close_pct = (self._high_arr[-3:] / self._close_arr[-3:]) <= 1 + high_pct
            is_pct_change_in_limit = (self._close_change_pct[-3:] < 0.05) & (self._close_change_pct[-3:] > 0)
            is_open_between = (self._today_open[-2:] >= (self._yesterday_close[-2:] * open_pos_pct +
                                                         self._yesterday_open[-2:] * (1 - open_pos_pct))) & \
                              (self._today_open[-2:] <= self._yesterday_close[-2:])
            return is_pct_change_in_limit.all() & is_open_between.all() & is_high_close_pct.all()
        else:

            is_high_close_pct = (self._high_arr[:, -3:] / self._close_arr[:, -3:]) <= 1 + high_pct
            is_pct_change_in_limit = (self._close_change_pct[:, -3:] < 0.05) & (self._close_change_pct[:, -3:] > 0)
            is_open_between = (self._today_open[:, -2:] >= (self._yesterday_close[:, -2:] * open_pos_pct +
                                                            self._yesterday_open[:, -2:] * (1 - open_pos_pct))) & \
                              (self._today_open[:, -2:] <= self._yesterday_close[:, -2:])

            return is_pct_change_in_limit.all(axis=1) & is_open_between.all(axis=1) & is_high_close_pct.all(axis=1)

    def three_crow(self, open_pos_pct=0.5, low_pct=0.012):

        if self._ndim == 1:
            is_low_close_pct = (self._close_arr[-3:] / self._low_arr[-3:]) <= 1 + low_pct
            is_pct_change_in_limit = (self._close_change_pct[-3:] > -1 * 0.05) & (self._close_change_pct[-3:] < 0)
            is_open_between = (self._today_open[-2:] <= (self._yesterday_open[-2:] * open_pos_pct +
                                                         self._yesterday_close[-2:] * (1 - open_pos_pct))) & \
                              (self._today_open[-2:] >= self._yesterday_close[-2:])
            return is_pct_change_in_limit.all() & is_open_between.all() & is_low_close_pct.all()
        else:

            is_low_close_pct = (self._close_arr[:, -3:] / self._low_arr[:, -3:]) <= 1 + low_pct
            is_pct_change_in_limit = (self._close_change_pct[:, -3:] > -1 * 0.05) & (self._close_change_pct[:, -3:] < 0)
            is_open_between = (self._today_open[:, -2:] <= (self._yesterday_open[:, -2:] * open_pos_pct +
                                                            self._yesterday_close[:, -2:] * (1 - open_pos_pct))) & \
                              (self._today_open[:, -2:] >= self._yesterday_close[:, -2:])
            return is_pct_change_in_limit.all(axis=1) & is_open_between.all(axis=1) & is_low_close_pct.all(axis=1)

    def multi_cannon(self, growth_pct_min=0.03):
        """
        多方炮
        需要四天数据
        """
        if self._ndim == 1:
            is_u_d_u = (self._close_change_pct[-3] > growth_pct_min) & \
                       (self._close_change_pct[-1] > growth_pct_min) & \
                       (self._close_change_pct[-2] < 0)

            # 昨天阴线收盘要大于前天的开盘价
            is_yesterday_great_bf_open = (self._close_arr[-2] > self._open_arr[-3])
            is_great_growth = (self._close_arr[-1] > self._close_arr[-3])

            return is_u_d_u & is_yesterday_great_bf_open & is_great_growth

        else:
            is_u_d_u = (self._close_change_pct[:, -3] > growth_pct_min) & \
                       (self._close_change_pct[:, -1] > growth_pct_min) & \
                       (self._close_change_pct[:, -2] < 0)

            is_yesterday_great_bf_open = self._close_arr[:, -2] > self._open_arr[:, -3]
            is_great_growth = self._close_arr[:, -1] > self._close_arr[:, -3]

            return is_u_d_u & is_yesterday_great_bf_open & is_great_growth

    def morning_start(self):
        if self._ndim == 1:
            condition_1 = self._close_arr[-3] / self._open_arr[-3] < 0.95
            condition_2 = self._open_arr[-2] < self._close_arr[-3]
            is_yesterday_cross_star = abs(self._open_arr[-2] - self._close_arr[-2]) / self._close_arr[-2] < 0.03
            is_today_growth = self._close_arr[-1] / self._open_arr[-1] > 1.05
            condition_3 = self._close_arr[-1] > self._close_arr[-3]

        else:
            condition_1 = self._close_arr[:, -3] / self._open_arr[:, -3] < 0.95
            condition_2 = self._open_arr[:, -2] < self._close_arr[:, -3]
            is_yesterday_cross_star = abs(self._open_arr[:, -2] - self._close_arr[:, -2]) / self._close_arr[:, -2] < 0.03
            is_today_growth = self._close_arr[:, -1] / self._open_arr[:, -1] > 1.05
            condition_3 = self._close_arr[:, -1] > self._close_arr[:, -3]

        return condition_1 & condition_2 & is_yesterday_cross_star & is_today_growth & condition_3

    def duck_head(self, min_period=8, mid_period=18, max_period=55):
        """
        上涨中继， 老鸭头
        :return:
        """
        E1 = self.moving_average(self._close_arr, n=mid_period)
        E2 = self.moving_average(self._close_arr, n=max_period)

        if self._ndim == 1:
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
                   is_mid_13_growth & condition_4 & f13.all() & condition_6.all() & \
                   condition_7.all() & condition_8 & condition_9

        elif self._ndim == 2:
            is_min_5_growth = np.sum(np.diff(E1[:, -min_period-1:-1], 1) > 0, axis=1) >= 6
            is_mid_today_growth = E1[:, -1] > E1[:, -2]
            is_mid_13_growth = np.sum(np.diff(E2[:, -mid_period:], 1) > 0, axis=1) >= 13
            f13 = (self._low_arr[:, -mid_period:] / E2[:, -mid_period:] - 1) < 0.1
            condition_6 = E1[:, -mid_period:] > E2[:, -mid_period:]
            condition_7 = self._close_arr[:, -min_period:] > E2[:, -min_period:]
            condition_8 = self._close_arr[:, -1] > E1[:, -1]
            condition_9 = E1[:, -1] / E2[:, -1] < 1.10

            return is_min_5_growth & is_mid_today_growth & \
                   is_mid_13_growth & f13.all(axis=1) & condition_6.all(axis=1) & \
                   condition_7.all(axis=1) & condition_8 & condition_9

    @staticmethod
    def moving_average(a, n=3):
        ndim = a.ndim
        if ndim == 1:
            ret = np.cumsum(a, dtype=float)
            ret[n:] = ret[n:] - ret[:-n]
            return ret[n - 1:] / n
        elif ndim == 2:
            ret = np.cumsum(a, dtype=float, axis=1)
            ret[:, n:] = ret[:, n:] - ret[:, :-n]
            return ret[:, n - 1:] / n

        else:
            raise ValueError('a.ndim must be in [1, 2]')


if __name__ == '__main__':
    aaa = Classical.three_red_soldiers(np.array([1., 5., 6.8], dtype='float'),
                                       np.array([7, 8, 9], dtype='float'),
                                       np.array([1, 2, 3], dtype='float'),
                                       np.array([6, 7, 8], dtype='float'))

    print(aaa)