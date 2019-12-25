# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019/12/25 8:54 PM
"""

import numpy as np
from ginkgo.core.classical_base import ClassicalBase
from ginkgo.core.analysis_util import zigzag

from ginkgo import classical_conf

EXT_DEPTH = classical_conf['find_corner']['ext_depth']
EXT_DEVIATION = classical_conf['find_corner']['ext_deviation']
EXT_BACKSTEP = classical_conf['find_corner']['ext_backstep']

W_FORM_VOLATILITY = classical_conf['w_form']['volatility']
W_FORM_COUNT_LIMIT = classical_conf['w_form']['count_limit']
M_FORM_VOLATILITY = classical_conf['m_form']['volatility']
M_FORM_COUNT_LIMIT = classical_conf['m_form']['count_limit']


class ComplexForm(ClassicalBase):
    def __init__(self, *args, date_index_arr, **kwargs):
        """
        只能单只股票进行计算
        :param args:
        :param date_index_arr: 行情对应的date array
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        self._body_high = None
        self._body_low = None
        self._date_index_arr = date_index_arr
        if self._ndim != 1:
            raise ValueError('input array ndim mast be 1')
        self._corner_index_list = None
        self._corner_with_start_end_list = None
        self._init_data()

    def _init_data(self):
        self._body_high = np.maximum(self._open_arr, self._close_arr)
        self._body_low = np.minimum(self._open_arr, self._close_arr)
        self._find_corner()
        self._corner_with_start_end_list = self._corner_index_with_start_end()

    def _find_corner(self,
                     ext_depth=EXT_DEPTH,
                     ext_deviation=EXT_DEVIATION,
                     ext_backstep=EXT_BACKSTEP):
        self._corner_index_list = zigzag(self._close_arr, ext_deviation=ext_deviation, ext_depth=ext_depth,
                                         ext_backstep=ext_backstep)
        return self._corner_index_list

    def _corner_index_with_start_end(self):
        index = self._corner_index_list[:]
        # 保证start, end在列表中
        if 0 not in self._corner_index_list:
            index.insert(0, 0)
        end = self._shape[0] - 1
        if end not in self._corner_index_list:
            index.append(end)
        return index

    def _corner_date_index(self, start=-5, end=None):
        i_index = self._corner_with_start_end_list[start:end]
        return self._date_index_arr[i_index].tolist()

    def w_form(self,
               volatility=W_FORM_VOLATILITY,
               count_limit=W_FORM_COUNT_LIMIT):
        index_with_start_end = self._corner_with_start_end_list
        if len(index_with_start_end) < 5:
            return False, None
        p0 = index_with_start_end[-1]
        p1 = index_with_start_end[-2]
        p2 = index_with_start_end[-3]
        p3 = index_with_start_end[-4]
        p4 = index_with_start_end[-5]

        first = (self._close_arr[p0] > self._close_arr[p1]) and \
                (abs(self._body_low[p1] - self._body_low[p3]) / self._body_low[p1]) < volatility  and \
                (self._body_high[p4] > self._body_high[p2]) and \
                (self._body_high[p0] > self._body_high[p2])

        if first:
            # 确保是高于p2的count_limit个bar以内
            count = 0
            for i in range(p1, p0+1):
                if self._body_high[i] > self._body_high[p2]:
                    count += 1
                    if count > count_limit:
                        return False, None
            corner_date_list = self._corner_date_index()
            return True, corner_date_list
        else:
            return False, None

    def m_form(self,
               volatility=M_FORM_VOLATILITY,
               count_limit=M_FORM_COUNT_LIMIT):
        index_with_start_end = self._corner_with_start_end_list
        if len(index_with_start_end) < 5:
            return False, None
        p0 = index_with_start_end[-1]
        p1 = index_with_start_end[-2]
        p2 = index_with_start_end[-3]
        p3 = index_with_start_end[-4]
        p4 = index_with_start_end[-5]

        first = (self._close_arr[p0] < self._close_arr[p1]) and \
                (abs(self._body_low[p1] - self._body_low[p3]) / self._body_low[p1]) < volatility and \
                (self._body_low[p4] < self._body_low[p2]) and \
                (self._body_low[p0] < self._body_low[p2])
        if first:
            # 确保是低于p2的count_limit个bar以内
            count = 0
            for i in range(p1, p0+1):
                if self._body_low[i] < self._body_low[p2]:
                    count += 1
                    if count > count_limit:
                        return False, None
            corner_date_list = self._corner_date_index()
            return True, corner_date_list
        else:
            return False, None
