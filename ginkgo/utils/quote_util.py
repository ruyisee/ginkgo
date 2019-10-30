# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-10-29 08:55
"""
from datetime import datetime
from functools import lru_cache
from ginkgo.utils.tushare_client import ts_client
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
    def load_calendar(market='CN'):

        if market == 'CN':
            return ts_client.trade_cal(is_open=1)['cal_date']
        else:
            raise NotImplementedError