# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019/12/26 9:29 AM
"""
from ginkgo.constant import Market
from ginkgo.data_local.data_proxy import DataProxy


class QuoteUtil:

    def __init__(self, market=Market.CN):
        self._market = market
        self._data_proxy = DataProxy(market=self._market)

    def get_symbols(self):
        return self._data_proxy.get_symbols()

    def get_daily_quote(self, start_date, end_date, br=True):
        pass

    def get_calendar(self, start_date, end_date=None):
        pass

    def get_real_date(self, dt, bar_count):
        pass
