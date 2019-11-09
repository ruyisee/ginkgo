# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-10-29 08:55
"""
from datetime import datetime
import time
from functools import lru_cache
import pandas as pd
from ginkgo.utils.tushare_client import ts_pro


class QuoteUtil:

    @staticmethod
    @lru_cache(4)
    def load_symbols(market='CN'):
        if market == 'CN':
            symbols = ts_pro.stock_basic(list_status='L')
            symbols.rename({'ts_code': 'code', 'market': 'board'}, inplace=True, axis=1)
        else:
            raise NotImplementedError
        return symbols

    @staticmethod
    def load_daily_hists_quote(codes, start_date, end_date, market='CN'):
        quote_list = []
        if market == 'CN':
            for code in codes:
                single = ts_pro.daily(ts_code=code, start_date=start_date, end_date=end_date)
                quote_list.append(single[['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'vol']])
                time.sleep(0.4)
        else:
            raise NotImplementedError

        data = pd.concat(quote_list, ignore_index=True)
        data.rename({'ts_code': 'code', 'vol': 'volume'}, inplace=True, axis=1)

        return data

    @staticmethod
    def load_calendar(start_date=None, end_date=None, market='CN'):
        if market == 'CN':
            return ts_pro.trade_cal(start_date=start_date, end_date=end_date, is_open=1)['cal_date'].to_list()
        else:
            raise NotImplementedError


if __name__ == '__main__':
    symbols = QuoteUtil.load_symbols()
    symbols = symbols.iloc[:5, 0]

    quote = QuoteUtil.load_daily_hists_quote(symbols, '20190101', '20190115')
    print(quote)
