# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-11-07 09:20
"""

import numpy as np
import pandas as pd


class BaseContract:
    pass


class StockContract(BaseContract):

    __slots__ = ['code', 'symbol', 'name', 'market', 'industry', 'board',
                 'list_date', 'lot_size', 'sid', 'area']

    def __init__(self, code, symbol, sid, name, market, industry, board, area=None, list_date=None, lot_size=1):
        self.code = code
        self.symbol = symbol
        self.name = name
        self.market = market
        self.industry = industry
        self.board = board
        self.area = area
        self.list_date = list_date
        self.lot_size = lot_size
        self.sid = sid


class Frame:

    __slots__ = ['arr', 'index', 'columns', 'symbol']

    def __init__(self, arr, index, columns, symbol):
        self.arr = arr
        self.index = index
        self.columns = columns
        self.symbol = symbol

    def to_dataframe(self):
        data = pd.DataFrame(self.arr, columns=self.columns)
        data['timestamp'] = self.index
        data['symbol'] = self.symbol
        return data

    def append(self, other):
        raise NotImplementedError


class SFrame:

    def __init__(self, frame_list=None):
        self.frame_dict = frame_list if frame_list else {}
        self.index = None
        self.columns = None

    def append(self, other):
        for frame in other.frame_dict.values():
            self.add(frame)

    def add(self, other: Frame):
        if (self.index is not None) and (self.columns is not None):
            if (other.index != self.index) or (other.columns != self.columns):
                raise ValueError('frame object mast be same index and columns')
        else:
            self.index = other.index
            self.columns = other.columns
        self.frame_dict[other.symbol] = other

    def to_dataframe(self):
        if not self.frame_dict:
            return pd.DataFrame()
        arr_list = []
        symbol_list = []
        for frame in self.frame_dict.values():
            arr_list.append(frame.arr)
            symbol_list.append(frame.symbol)

        index_obj = pd.MultiIndex.from_product([symbol_list, self.index], names=['symbol', 'timestamp']).swaplevel(0, 1)

        all_arr = np.concatenate(arr_list)

        data = pd.DataFrame(all_arr, index=index_obj, columns=self.columns)
        return data
