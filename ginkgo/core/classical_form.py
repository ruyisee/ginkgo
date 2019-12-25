
# -*- coding:utf-8 -*-
"""
@author: fsksf

@since: 2019-10-25 20:59

计算经典形态
"""
import numpy as np
from ginkgo.core.classical_base import ClassicalBase
from ginkgo.core.analysis_util import moving_average, current_position
from ginkgo import classical_conf

np.seterr(divide='ignore', invalid='ignore')

THREE_RED_SOLDIERS_GROWTH_MAX_LIMIT = classical_conf['three_red_soldiers']['close_growth_max_limit']
THREE_RED_SOLDIERS_GROWTH_MIN_LIMIT = classical_conf['three_red_soldiers']['close_growth_min_limit']
THREE_RED_SOLDIERS_OPEN_PCT_MIN_LIMIT = classical_conf['three_red_soldiers']['open_pct_min_limit']
THREE_RED_SOLDIERS_HIGH_PCT_MAX_LIMIT = classical_conf['three_red_soldiers']['high_pct_max_limit']

THREE_CROW_OPEN_POS_PCT = classical_conf['three_crow']['open_pos_pct']
THREE_CROW_LOW_PCT = classical_conf['three_crow']['low_pct']

MULTI_CANNON_GROWTH_PCT_MIN = classical_conf['multi_cannon']['growth_pct_min']

MORNING_STAR_BODY_CHANGE_PCT_3 = classical_conf['morning_star']['body_change_pct_3']
MORNING_STAR_BODY_CHANGE_PCT_2 = classical_conf['morning_star']['body_change_pct_2']
MORNING_STAR_BODY_CHANGE_PCT_1 = classical_conf['morning_star']['body_change_pct_1']

DUCK_HEAD_MIN_PERIOD = classical_conf['duck_head']['min_period']
DUCK_HEAD_MIN_FALL_COUNT = classical_conf['duck_head']['min_fall_count']
DUCK_HEAD_MID_PERIOD = classical_conf['duck_head']['mid_period']
DUCK_HEAD_MID_GROWTH_COUNT = classical_conf['duck_head']['mid_growth_count']
DUCK_HEAD_MAX_PERIOD = classical_conf['duck_head']['max_period']
DUCK_HEAD_LOW_MA_RATIO = classical_conf['duck_head']['low_ma_ratio']

GOLDEN_CROSS_MIN_PERIOD = classical_conf['golden_cross']['min_period']
GOLDEN_CROSS_MID_PERIOD = classical_conf['golden_cross']['mid_period']
GOLDEN_CROSS_MAX_PERIOD = classical_conf['golden_cross']['max_period']

DEAD_CROSS_MIN_PERIOD = classical_conf['dead_cross']['min_period']
DEAD_CROSS_MID_PERIOD = classical_conf['dead_cross']['mid_period']
DEAD_CROSS_MAX_PERIOD = classical_conf['dead_cross']['max_period']


class Classical(ClassicalBase):

    def __init__(self, *args, date_index_arr, **kwargs):
        super().__init__(*args, **kwargs)
        self._close_growth = None  # 增量
        self._yesterday_close = None
        self._date_index_arr = date_index_arr
        self._init_data()

    def _init_data(self):
        self._close_growth = np.diff(self._close_arr, 1, 0)

        self._yesterday_close = self._close_arr[:-1]
        self._yesterday_open = self._open_arr[:-1]
        self._today_open = self._open_arr[1:]

        self._close_change_pct = self._close_growth / self._yesterday_close
        self._current_position_mask = current_position(self._close_arr)

    def _get_form_date(self, n):
        return self._date_index_arr[n]

    def three_red_soldiers(self,
                           growth_max_limit=THREE_RED_SOLDIERS_GROWTH_MAX_LIMIT,
                           growth_min_limit=THREE_RED_SOLDIERS_GROWTH_MIN_LIMIT,
                           open_pct_min_limit=THREE_RED_SOLDIERS_OPEN_PCT_MIN_LIMIT,
                           high_pct_max_limit=THREE_RED_SOLDIERS_HIGH_PCT_MAX_LIMIT):
        """
        1、今天昨天前天三日收盘价持续三日走高；
        2、三日涨幅均在5%以内；
        3、开盘价位于前一天实体的上半部分
        4、最高价/收盘价 < 1.012
        :param growth_max_limit: 每日增长最大限制
        :param growth_min_limit: 每日增长最小限制
        :param open_pct_min_limit:开盘价在昨日实体百分比位置
        :param high_pct_max_limit:上影线最大比例限制
        :return:
        """

        is_pct_change_in_limit = (self._close_change_pct[-3:] < growth_max_limit) & \
                                 (self._close_change_pct[-3:] > growth_min_limit)
        is_open_between = (self._today_open[-2:] >= (self._yesterday_close[-2:] * open_pct_min_limit +
                                                     self._yesterday_open[-2:] * (1 - open_pct_min_limit))) & \
                          (self._today_open[-2:] <= self._yesterday_close[-2:])
        is_daily_growth = self._close_arr[-3:] > self._open_arr[-3:]
        is_high_close_pct = (self._high_arr[-3:] / self._close_arr[-3:]) <= 1 + high_pct_max_limit
        mask = is_pct_change_in_limit.all(axis=0) & is_open_between.all(axis=0) & \
               is_high_close_pct.all(axis=0) & is_daily_growth.all(axis=0) & \
               (self._current_position_mask > 0)
        symbols = self._filter_symbols(mask)
        start_date = self._get_form_date(-3)
        end_date = self._get_form_date(-1)
        return symbols, (start_date, end_date)

    def three_crow(self,
                   open_pos_pct=THREE_CROW_OPEN_POS_PCT,
                   low_pct=THREE_CROW_LOW_PCT):
        is_low_close_pct = (self._close_arr[-3:] / self._low_arr[-3:]) <= 1 + low_pct
        is_pct_change_in_limit = (self._close_change_pct[-3:] > -1 * 0.05) & (self._close_change_pct[-3:] < 0)
        is_open_between = (self._today_open[-2:] <= (self._yesterday_open[-2:] * open_pos_pct +
                                                     self._yesterday_close[-2:] * (1 - open_pos_pct))) & \
                          (self._today_open[-2:] >= self._yesterday_close[-2:])

        mask = is_pct_change_in_limit.all(axis=0) & is_open_between.all(axis=0) & is_low_close_pct.all(axis=0) & \
               (self._current_position_mask < 0)
        symbols = self._filter_symbols(mask)
        start_date = self._get_form_date(-3)
        end_date = self._get_form_date(-1)
        return symbols, (start_date, end_date)

    def multi_cannon(self, growth_pct_min=MULTI_CANNON_GROWTH_PCT_MIN):
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
        mask = is_u_d_u & is_yesterday_great_bf_open & is_great_growth & \
               (self._current_position_mask > 0)
        symbols = self._filter_symbols(mask)
        start_date = self._get_form_date(-3)
        end_date = self._get_form_date(-1)
        return symbols, (start_date, end_date)

    def morning_star(self,
                     body_change_pct_3=MORNING_STAR_BODY_CHANGE_PCT_3,
                     body_change_pct_2=MORNING_STAR_BODY_CHANGE_PCT_2,
                     body_change_pct_1=MORNING_STAR_BODY_CHANGE_PCT_1):
        """

        :param body_change_pct_3: 倒数第三天下跌百分比
        :param body_change_pct_2: 倒数第二天star 涨跌不超过
        :param body_change_pct_1: 倒数第一天上涨百分比
        :return:
        """
        condition_1 = self._close_arr[-3] / self._open_arr[-3] < 1 - body_change_pct_3
        condition_2 = self._open_arr[-2] < self._close_arr[-3]
        is_yesterday_cross_star = abs(self._open_arr[-2] - self._close_arr[-2]) / self._close_arr[-2] < body_change_pct_2
        is_today_growth = self._close_arr[-1] / self._open_arr[-1] > 1 + body_change_pct_1
        condition_3 = self._close_arr[-1] > self._close_arr[-3]

        mask = condition_1 & condition_2 & is_yesterday_cross_star & is_today_growth & condition_3
        symbols = self._filter_symbols(mask)

        start_date = self._get_form_date(-3)
        end_date = self._get_form_date(-1)
        return symbols, (start_date, end_date)

    def duck_head(self,
                  min_period=DUCK_HEAD_MIN_PERIOD,
                  mid_period=DUCK_HEAD_MID_PERIOD,
                  max_period=DUCK_HEAD_MAX_PERIOD,
                  min_fall_count=DUCK_HEAD_MIN_FALL_COUNT,
                  mid_growth_count=DUCK_HEAD_MID_GROWTH_COUNT,
                  low_ma_ratio=DUCK_HEAD_LOW_MA_RATIO):
        """
        上涨中继， 老鸭头
        :return:
        """
        E1 = moving_average(self._close_arr, n=mid_period)
        E2 = moving_average(self._close_arr, n=max_period)

        # 1、前8日中满足“E1<1日前的E1”的天数>=6
        is_min_5_growth = np.sum(np.diff(E1[-min_period - 1:-1], 1, 0) < 0, 0) >= min_fall_count
        # 2、 今天的E1 > 昨天的E1
        is_mid_today_growth = E1[-1] > E1[-2]
        # 3、最近18天中满足“E2>1日前的E2”的天数>=13
        is_mid_13_growth = np.sum(np.diff(E2[-mid_period:], 1, 0) > 0, 0) >= mid_growth_count
        # 4、 今天的E2>昨天的E2
        condition_4 = E2[-1] > E2[-2]
        f13 = (self._low_arr[-mid_period:] / E2[-mid_period:] - 1) <= low_ma_ratio
        # 6、最近18日都满足“E1>E2”
        condition_6 = E1[-mid_period:] > E2[-mid_period:]
        condition_7 = self._close_arr[-min_period:] > E2[-min_period:]
        condition_8 = self._close_arr[-1] > E1[-1]
        condition_9 = E1[-1] / E2[-1] < 1.10
        # 10. 前8日满足|(E1-E2)/E2|<0.05的天数>=6
        # condition_10 = np.sum(np.abs(E1[-1 * min_period:] - E2[-1 * min_period:]) / E2[-1 * min_period:] < 0.05, 0) >= min_fall_count
        mask = is_min_5_growth & is_mid_today_growth & \
               is_mid_13_growth & condition_4 & f13.all(axis=0) & condition_6.all(axis=0) & \
               condition_7.all(axis=0) & condition_8 & condition_9
        symbols = self._filter_symbols(mask)
        start_date = None
        end_date = self._get_form_date(-1)
        return symbols, (start_date, end_date)

    def rise_wrap_fall(self):
        """
        阳包阴
        :return:
        """
        is_yesterday_fall = (self._close_arr[-2] < self._close_arr[-3]) & (self._close_arr[-2] < self._open_arr[-2])
        is_today_rise = (self._close_arr[-1] > self._close_arr[-2]) & (self._close_arr[-1] > self._open_arr[-1])
        is_wrap = (self._close_arr[-1] > self._open_arr[-2]) & (self._open_arr[-1] < self._close_arr[-2])

        E1 = moving_average(self._close_arr, n=60)
        position = self._close_arr[-1] < E1[-1] * (1 - 0.2)
        mask = is_yesterday_fall & is_today_rise & is_wrap & position
        symbols = self._filter_symbols(mask)
        start_date = self._get_form_date(-2)
        end_date = self._get_form_date(-1)
        return symbols, (start_date, end_date)

    def fall_wrap_raise(self):
        """
        阴包阳
        :return:
        """
        is_yesterday_raise = (self._close_arr[-2] > self._close_arr[-3]) & (self._close_arr[-2] > self._open_arr[-2])
        is_today_fall = (self._close_arr[-1] < self._close_arr[-2]) & (self._close_arr[-1] < self._open_arr[-1])
        is_wrap = (self._close_arr[-1] < self._open_arr[-2]) & (self._open_arr[-1] > self._close_arr[-2])

        E1 = moving_average(self._close_arr, n=60)
        position = self._close_arr[-1] > E1[-1] * (1 + 0.2)
        mask = is_yesterday_raise & is_today_fall & is_wrap & position
        symbols = self._filter_symbols(mask)
        start_date = self._get_form_date(-2)
        end_date = self._get_form_date(-1)
        return symbols, (start_date, end_date)

    def rise_pregnant_line(self):
        is_yesterday_fall = (self._close_arr[-2] < self._close_arr[-3]) & (self._close_arr[-2] < self._open_arr[-2])
        is_today_rise = (self._close_arr[-1] > self._close_arr[-2]) & (self._close_arr[-1] > self._open_arr[-1])
        is_wrap = (self._close_arr[-1] < self._open_arr[-2]) & (self._open_arr[-1] > self._close_arr[-2])
        E1 = moving_average(self._close_arr, n=60)
        position = self._close_arr[-1] < E1[-1] * (1 - 0.2)
        mask = is_yesterday_fall & is_today_rise & is_wrap & position
        symbols = self._filter_symbols(mask)
        start_date = self._get_form_date(-2)
        end_date = self._get_form_date(-1)
        return symbols, (start_date, end_date)

    def golden_cross(self,
                     min_period=GOLDEN_CROSS_MIN_PERIOD,
                     mid_period=GOLDEN_CROSS_MID_PERIOD,
                     max_period=GOLDEN_CROSS_MAX_PERIOD):
        E1 = moving_average(self._close_arr, min_period)
        E2 = moving_average(self._close_arr, mid_period)
        E3 = moving_average(self._close_arr, max_period)

        condition_1 = E1[-1] > E2[-1]
        condition_2 = E1[-2] < E2[-2]
        condition_3 = E2[-1] > E3[-1]
        condition_4 = E2[-2] < E3[-2]
        mask = condition_1 & condition_2 & condition_3 & condition_4 & \
               (self._current_position_mask > 0)
        symbols = self._filter_symbols(mask)
        start_date = None
        end_date = self._get_form_date(-1)
        return symbols, (start_date, end_date)

    def dead_cross(self,
                   min_period=DEAD_CROSS_MIN_PERIOD,
                   mid_period=DEAD_CROSS_MID_PERIOD,
                   max_period=DEAD_CROSS_MAX_PERIOD):
        E1 = moving_average(self._close_arr, min_period)
        E2 = moving_average(self._close_arr, mid_period)
        E3 = moving_average(self._close_arr, max_period)

        # 1、今日MA5<今日MA10；
        condition_1 = E1[-1] < E2[-1]
        # 2、昨日MA5>今日MA10；
        condition_2 = E1[-2] > E2[-2]
        # 3、今日MA10<今日MA20；
        condition_3 = E2[-1] < E3[-1]
        # 4、昨日MA10 > 今日MA20；
        condition_4 = E2[-2] > E3[-2]
        mask = condition_1 & condition_2 & condition_3 & condition_4 & \
                   (self._current_position_mask < 0)
        symbols = self._filter_symbols(mask)
        start_date = None
        end_date = self._get_form_date(-1)
        return symbols, (start_date, end_date)
