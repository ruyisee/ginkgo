# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-11-09 16:15
"""
from ginkgo import PROJECT_CONFIG_DIR
from ginkgo.data_local.source_quote import QuoteModel


class DataProxy:

    def __init__(self, catgory='stock', market='CN'):
        self._daily_quote = QuoteModel(PROJECT_CONFIG_DIR, catgory=catgory, freq='daily', market=market)
        self._daily_quote.load('r')

        # method proxy
        self.get_calendar = self._daily_quote.get_calendar
        self.get_symbols = self._daily_quote.contracts_filter
        self.get_date_offset = self._daily_quote.get_date_offset
        self.get_valid_date = self._daily_quote.get_valid_date

    def get_daily_hist(self, symbol, start_date, end_date, fields_list=None, br=False):
        frame = self._daily_quote.get_symbol_data(symbol, start_date, end_date, fields_list)

        return frame

    def get_daily_hists(self, symbols, start_date, end_date, fields_list=None, br=False):
        sframe = self._daily_quote.get_symbols_data(symbols, start_date, end_date, fields_list)
        return sframe

    def get_split(self, symbols, start_date, end_date):
        pass


if __name__ == '__main__':
    dp = DataProxy()
    df = dp.get_daily_hist('000023.SZ', 20190102, 20191102)
    print(df.to_dataframe())
    df = dp.get_daily_hist('000563.SZ', 20190102, 20191102)
    print(df.to_dataframe())