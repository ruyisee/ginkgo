# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-11-21 08:43
"""
import time
from functools import lru_cache
from requests.exceptions import ConnectionError
import pandas as pd
from ginkgo.utils.logger import logger
from ginkgo.utils.tushare_client import ts_pro


class FundmentalUtil:

    @staticmethod
    def load_split(codes, start_date, end_date, market='CN'):
        retry = 5
        split_list = []
        if market == 'CN':
            for code in codes:
                retry_count = 0
                while retry_count < retry:
                    time.sleep(0.6)
                    retry_count += 1
                    try:
                        single = ts_pro.adj_factor(ts_code=code, start_date=start_date, end_date=end_date)
                        single = single.set_index('trade_date')['adj_factor'].sort_index()
                        factors = single.shift(1) / single
                        factors = factors[factors != 1.0].dropna()
                        factors = factors.to_frame()
                        factors['symbol'] = code
                        split_list.append(factors)
                        break
                    except ConnectionError as e:
                        if retry_count == retry:
                            raise
                        else:
                            time.sleep(3)
        else:
            raise NotImplementedError

        data = pd.concat(split_list)
        data.rename({'ts_code': 'symbol'}, inplace=True, axis=1)
        data.reset_index(inplace=True)
        data['trade_date'] = data['trade_date'].astype('uint32')
        return data


if __name__ == '__main__':
    fct = FundmentalUtil.load_split(['600547.SH', ], 20100101, 20191111)
    print(fct)
    fct['trade_date'] = fct['trade_date'].astype('uint32')
    fct_cumprod = fct.set_index('trade_date').sort_index()['adj_factor'][::-1].cumprod()[::-1]
    print(fct_cumprod)
    from ginkgo.data_local.data_proxy import DataProxy
    dp = DataProxy()
    prc = dp.get_daily_hist('600547.SH', 20100101, 20191111).to_dataframe()
    print(prc)

    close = prc.set_index('timestamp')['close']
    print(close)
    fct_cumprod = fct_cumprod.reindex(close.index, method='bfill').fillna(method='bfill').fillna(value=1.0)
    print(fct_cumprod)
    close_br = close * fct_cumprod
    print(close_br)

