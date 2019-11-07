# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-11-07 10:14
"""
import os

from ginkgo.data_local.source_index import RowIndex
from ginkgo.data_local.ingester import StandardQuoteIngester
from ginkgo.data_local.interface import LocalDataBase


class QuoteModel(LocalDataBase):

    def __init__(self, base_path, fields=('open', 'high', 'low', 'close', 'vol'), catgory='stock', market='CN'):

        self._base_path = base_path
        self._market = market
        self._fields = fields
        self._row_index = RowIndex(base_path, catgory=catgory, market=market)
        self._fields_data_path = \
            {field: os.path.join(base_path, f'{catgory.lower()}/{market.lower()}/{field}') for field in self._fields}

    def ingest(self, symbols, start_date, end_date):
        quote = StandardQuoteIngester.ingest_daily_hists_quote(symbols, start_date, end_date)
        return quote

    def init(self):
        pass

    def update(self, end_date):
        pass

    def save(self):
        pass

    def load(self):
        pass