# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-11-14 20:09
"""
import pandas as pd
from ginkgo.utils.tushare_client import ts_pro

start_date = 20190101
end_date = 20191101
quote_list = []
symbol_list = ['000001.SZ', '600600.SH', '600703.SH']

for symbol in symbol_list:
    symbol_df = ts_pro.daily(ts_code=symbol, start_date=start_date, end_date=end_date)
    quote_list.append(symbol_df)

quote_df = pd.concat(quote_list)
quote_df.rename({'ts_code': 'symbol', 'trade_date': 'timestamp', 'vol': 'volume'}, inplace=True, axis=1)
quote_df.sort_values(['symbol', 'timestamp'], inplace=True)
quote_df.to_csv('./csv/cn_daily_stock_quote.csv', index=False)
