# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-11-20 08:24
"""
import os
from ginkgo.data_local.interface import LocalDataBase
from ginkgo.data_local.fundmental_ingester import StandardFundamentalIngester
from ginkgo.data_local.data_proxy import DataProxy
from ginkgo.utils.logger import logger


class Fundamental(LocalDataBase):

    def __init__(self, base_path, catgory='stock', market='CN', data_proxy: DataProxy):
        self._base_path = base_path
        self._catgory = catgory.lower()
        self._market = market.upper()
        self.db_path = os.path.join(base_path, self._catgory, self._market)
        self._data_proxy = data_proxy

    def ingest(self, symbols, start_date, end_date):
        logger.info('fundamental ingest start')

        if symbols is None:
            symbols = self._data_proxy.get_symbols

        fetch_chunk_num = 50
        symbols_len = len(symbols)
        all_chunk_num = symbols_len // fetch_chunk_num + 1

        for i in range(0, len(symbols), fetch_chunk_num):
            logger.info(f'ingest split: {i // fetch_chunk_num + 1}/{all_chunk_num}')
            period_symbols = symbols[i: i+fetch_chunk_num]
            yield StandardFundamentalIngester.ingest_split(period_symbols, start_date, end_date)


    def get_split(self, symbols, start_date, end_date):
        pass
