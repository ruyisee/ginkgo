# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-10-29 08:55
"""
from datetime import datetime
from functools import lru_cache
import tushare as ts


class QuoteUtil:

    @staticmethod
    @lru_cache(4)
    def load_symbols(market='CN'):
        if market == 'CN':
            return ts.get_hs300s()['code'].to_list()
        else:
            raise NotImplementedError

    @staticmethod
    def load_daily_quote(symbols, start_date, end_date, market='CN'):
        if market == 'CN':
            return ts.get_hists(symbols, start_date, end_date)
        else:
            raise NotImplementedError

    @staticmethod
    def load_calendar(start_date='2015-01-01', end_date=None, market='CN'):

        if market == 'CN':
            return ts.get_hist_data(code='000001', start=start_date, end=end_date).index.to_series().apply(
                lambda s: datetime.strptime(s, '%Y-%M-%d')
            )
        else:
            raise NotImplementedError