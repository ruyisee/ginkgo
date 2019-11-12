# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-10-29 08:55
"""
import time
from functools import lru_cache
from requests.exceptions import ConnectionError
import pandas as pd
from ginkgo.utils.logger import logger
from ginkgo.utils.tushare_client import ts_pro


class QuoteUtil:

    @staticmethod
    @lru_cache(4)
    def load_basic(market='CN'):
        if market == 'CN':
            contracts = ts_pro.stock_basic(list_status='L')
            contracts.rename({'symbol': 'code', 'ts_code': 'symbol', 'market': 'board'}, inplace=True, axis=1)
        else:
            raise NotImplementedError
        return contracts

    @staticmethod
    def load_daily_hists_v(codes, start_date, end_date, market='CN'):
        retry = 5
        quote_list = []
        if market == 'CN':
            for code in codes:
                retry_count = 0
                while retry_count < retry:
                    time.sleep(0.6)
                    retry_count += 1
                    try:
                        single = ts_pro.daily(ts_code=code, start_date=start_date, end_date=end_date)
                        quote_list.append(single[['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'vol']])
                        break
                    except ConnectionError as e:
                        if retry_count == retry:
                            raise
                        else:
                            time.sleep(3)
        else:
            raise NotImplementedError

        data = pd.concat(quote_list, ignore_index=True)
        data.rename({'ts_code': 'symbol', 'vol': 'volume'}, inplace=True, axis=1)
        return data

    @staticmethod
    def load_daily_hists_h(codes, trade_dates, market):
        retry = 5
        quote_list = []
        ts_codes = ','.join(codes)
        if market == 'CN':
            for trade_date in trade_dates:
                retry_count = 0
                while retry_count < retry:
                    time.sleep(0.6)
                    retry_count += 1
                    try:
                        single = ts_pro.daily(ts_code=ts_codes, trade_date=trade_date)
                        quote_list.append(single[['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'vol']])
                        break
                    except ConnectionError as e:
                        if retry_count == retry:
                            raise
                        else:
                            time.sleep(3)
        else:
            raise NotImplementedError

        data = pd.concat(quote_list, ignore_index=True)
        data.rename({'ts_code': 'symbol', 'vol': 'volume'}, inplace=True, axis=1)
        return data

    @staticmethod
    def load_calendar(start_date=None, end_date=None, market='CN'):
        if market == 'CN':
            calendar = ts_pro.trade_cal(start_date=start_date, end_date=end_date, is_open=1)['cal_date'].to_list()
            return [int(c) for c in calendar]
        else:
            raise NotImplementedError


if __name__ == '__main__':
    symbols = QuoteUtil.load_basic()
    symbols = symbols.iloc[:5, 0]

    quote = QuoteUtil.load_daily_hists_v(symbols, '20190101', '20190115')
    print(quote)
