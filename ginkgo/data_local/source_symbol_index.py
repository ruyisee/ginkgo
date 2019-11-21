# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-11-09 22:00
"""
import os

import pandas as pd

from ginkgo.core.model import StockContract
from ginkgo.data_local.quote_ingester import StandardQuoteIngester
from ginkgo.data_local.interface import Index
from ginkgo.utils.logger import logger


class ColSymbolIndex(Index):
    def __init__(self, *args, chunks_s_num=300, **kwargs):
        super().__init__(*args, **kwargs)
        self._chunks_s_num = chunks_s_num
        self._index_path = \
            os.path.join(self._base_path, f'meta/col_symbol_index.csv')
        self.check_file(self._index_path)
        self._stock_contract_list = []
        self._symbol_contract_dict = {}
        self._contract_df = None

    def ingest(self):
        logger.info('ingest symbol info')
        return StandardQuoteIngester.ingest_basic(self._market)

    def init(self):
        logger.info('init symbol info')
        col_df = self.ingest()
        self.save(col_df)
        self.load()

    def update(self):
        self.load()
        logger.info('updating contract')
        new = self.ingest()
        old = self._contract_df['symbol']
        to_update_df = new.set_index('symbol').drop(old).reset_index()
        if not to_update_df.empty:
            logger.info(f'update contracts {to_update_df["symbol"].to_list()}')
            self._contract_df = self._contract_df.append(to_update_df)
            self.save(self._contract_df)
            self.load()
        else:
            logger.info('no new contracts to update')

    def save(self, data: pd.DataFrame):
        logger.info('saving symbol info')
        data.to_csv(self._index_path, index=False, mode='w+')

    def load(self):
        logger.info('loading symbol info')
        self._stock_contract_list = []
        self._symbol_contract_dict = {}
        self._contract_df = pd.read_csv(self._index_path, dtype='str')
        for i, row in self._contract_df.iterrows():
            sc = StockContract(code=row.code, symbol=row.symbol, sid=i, name=row.name, market=self._market,
                               industry=row.industry, board=row.board, area=row.area, list_date=row.list_date)

            self._stock_contract_list.append(sc)
            self._symbol_contract_dict[row.symbol] = sc

    def contract_from_symbol(self, symbol, error='ignore'):
        try:
            return self._symbol_contract_dict[symbol]
        except KeyError as e:
            if error == 'ignore':
                return None
            raise ValueError(f'symbol `{symbol}` not exist')

    def i_of(self, symbol, error='ignore'):
        try:
            return self.contract_from_symbol(symbol, error).sid
        except AttributeError as e:
            if error == 'ignore':
                return None
            raise

    def o_of(self, i):
        return self._stock_contract_list[i]

    def chunk_id(self, i):
        return i // self._chunks_s_num

    def chunk_sid(self, i):
        return i % self._chunks_s_num

    @property
    def symbols(self):
        return list(self._symbol_contract_dict.keys())

    @property
    def codes(self):
        return self._contract_df['code'].to_list()

    def contracts_filter(self, industry=None, area=None, board=None, symbol=True):
        if (industry is None) & (area is None) & (board is None):
            return self._stock_contract_list[:]

        industry_mask = True
        area_mask = True
        board_mask = True
        if industry is not None:
            industry_mask = self._contract_df['industry'] == industry
        if area is not None:
            area_mask = self._contract_df['area'] == area
        if board is not None:
            board_mask = self._contract_df['board'] == board

        mask = industry_mask & area_mask & board_mask

        selected = self._contract_df.iloc[mask]['symbol']
        if symbol:
            return selected.to_list()
        contracts = []
        for c in selected:
            obj = self.contract_from_symbol(c)
            contracts.append(obj)
        return contracts