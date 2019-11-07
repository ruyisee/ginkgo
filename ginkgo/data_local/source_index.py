# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-11-04 19:18
"""

import os
import pickle
import pandas as pd
from ginkgo.data_local.ingester import StandardQuoteIngester
from ginkgo.core.model import StockContract
from ginkgo.data_local.interface import Index


class RowIndex(Index):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._index_path = \
            os.path.join(self.base_path, f'{self._catgory}/{self._market}/meta/row_index.plk')

    def ingest(self, start_date=None, end_date=None):
        return StandardQuoteIngester.ingest_calender(start_date, end_date, self._market)

    def init(self, start_date, end_date):
        calendar_list = self.ingest(start_date, end_date)
        self.save(calendar_list)

    def update(self, end_date):
        pass

    def load(self):

        self._name_list = pickle.load(self._index_path)
        self._name_i_map = {}
        for i, name in enumerate(self._name_list):
            self._name_i_map[name] = i
        self._latest_date = self._name_list[-1]

    def save(self, data):
        pickle.dump(data, self._index_path)


class ColIndex(Index):

    def __index__(self, *args, chunks_s_num=300, **kwargs):
        super().__init__(*args, **kwargs)
        self._chunks_s_num = chunks_s_num

        self._stock_contract_list = []
        self._symbol_contract_dict = {}
        self._contract_df = None

    def ingest(self):
        return StandardQuoteIngester.ingest_symbols(self._market)

    def init(self):
        col_df = self.ingest()
        self.save(col_df)

    def save(self, data: pd.DataFrame):
        data.to_pickle(self._index_path)

    def load(self):
        self._contract_df = pd.read_pickle(self._index_path)
        for i, row in self._contract_df.iterrows():
            sc = StockContract(code=row.code, symbol=row.symbol, sid=i, name=row.name, market=row.market,
                               industry=row.industry, board=row.board, area=row.area, list_date=row.list_date)

            self._stock_contract_list.append(sc)
            self._symbol_contract_dict[row.symbol] = sc

    def contract_of_symbol(self, symbol):
        return self._symbol_contract_dict[symbol]

    def iloc_of(self, symbol):
        return self.contract_of_symbol(symbol).sid

    def loc_of(self, i):
        return self._stock_contract_list[i]


