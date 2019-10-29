# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-10-29 08:46
"""

from functools import lru_cache
from ginkgo.utils.quote_util import QuoteUtil


class BaseCalcManager:

    @staticmethod
    def load_quote(symbols, start_date, end_date, market='CN'):
        return QuoteUtil.load_daily_quote(symbols, start_date, end_date, market=market)

    def run(self, roll=False):
        raise NotImplementedError

    def calc(self, data):
        raise NotImplementedError

    @staticmethod
    @lru_cache(4, False)
    def load_calendar(market='CN'):
        return QuoteUtil.load_calendar(market=market)

    def get_real_trading_date(self, dt, bar_count, market='CN'):
        calendar_series = self.load_calendar(market=market)
        try:
            if bar_count > 0:
                return calendar_series[calendar_series <= dt].iloc[-1 * bar_count].to_pydatetime()
            else:
                return calendar_series[calendar_series >= dt].iloc[-1 * bar_count].to_pydatetime()
        except IndexError:
            raise IndexError(f'bar count before {dt} is  less than {bar_count}')

    @staticmethod
    def load_symbols(market='CN'):
        return QuoteUtil.load_symbols(market)

    @staticmethod
    def save(data):
        print(data)
