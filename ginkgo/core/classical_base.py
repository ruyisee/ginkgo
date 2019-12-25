# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019/12/25 7:58 PM
"""

import numpy as np


class ClassicalBase:
    def __init__(self, open_arr, high_arr, low_arr, close_arr, volume_arr, symbol_arr):
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
        self._symbols = np.array(symbol_arr)
        self._ndim = 1
        self._shape = None
        self._check_data()

    def _check_data(self):
        try:
            if not (self._open_arr.shape == self._high_arr.shape == self._low_arr.shape ==
                    self._close_arr.shape == self._volume_arr.shape):
                raise ValueError('All inputs must be the same shape')
        except AttributeError as e:
            raise ValueError('All inputs must be of type numpy.array')

        self._ndim = self._open_arr.ndim
        self._shape = self._open_arr.shape
        if self._ndim > 2:
            raise ValueError('All inputs ndim must be 1 or 2')

    def _filter_symbols(self, mask):
        if isinstance(mask, (bool, np.bool_)):
            return bool(mask)
        symbols = self._symbols[mask]
        if isinstance(symbols, np.ndarray):
            symbols = symbols.tolist()
        return symbols
