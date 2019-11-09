# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-11-07 10:14
"""
import os
import numpy as np

from ginkgo.data_local.source_index import RowDateIndex, ColSymbolIndex
from ginkgo.data_local.ingester import StandardQuoteIngester
from ginkgo.data_local.interface import LocalDataBase
from ginkgo.data_local.fields import fields_manager, fields_dict
from ginkgo.utils.logger import logger


class QuoteModel(LocalDataBase):

    def __init__(self, base_path, fields_dict=fields_dict,
                 chunks_s_num=300, catgory='stock', market='CN'):

        self._base_path = base_path
        self._market = market
        self._fields_dict = fields_dict
        self._date_index = RowDateIndex(base_path, catgory=catgory, market=market)
        self._chunks_s_num = chunks_s_num
        self._symbol_index = ColSymbolIndex(base_path, chunks_s_num=chunks_s_num, catgory=catgory, market=market)
        self._fields_dir_path = \
            {field: os.path.join(base_path, f'{catgory.lower()}/{market.lower()}/{field.name}')
             for field in self._fields_dict.values()}
        self._check_dir(self._fields_dir_path.values())
        self._memmap_files_dict = {}

    def _check_dir(self, dirs):
        for d in dirs:
            self.check_file(d, is_dir=True)

    def ingest(self, codes, start_date, end_date):
        logger.info(f'quote ingest start')

        if codes is None:
            codes = self._symbol_index.codes

        fetch_chunk_num = 50
        codes_len = len(codes)
        all_chunk_num = codes_len // fetch_chunk_num + 1

        if codes is None:
            codes = self._symbol_index.codes
        for i in range(0, len(codes), fetch_chunk_num):
            logger.info(f'ingest quote: {i // fetch_chunk_num + 1}/{all_chunk_num}')
            period_codes = codes[i: i+fetch_chunk_num]
            yield StandardQuoteIngester.ingest_daily_hists_quote(period_codes, start_date, end_date)

    def init(self, codes, start_date, end_date):
        self._date_index.init(start_date, end_date)
        self._symbol_index.init()
        self.load(mode='w+')
        for quote in self.ingest(None, start_date, end_date):
            print(quote)
            self.save(quote)

    def update(self, end_date):
        pass

    def save(self, data):
        data['sid'] = sids = data.code.apply(self._symbol_index.i_of)
        data['did'] = data.trade_date.apply(self._date_index.i_of)
        data['chunk_id'] = sids // self._chunks_s_num               # 保存到第几块数据
        data['chunk_sid'] = sids % self._chunks_s_num           # 数据symbol在块内的索引
        data.dropna(how='any', inplace=True)
        logger.debug('[daily_bar_util] saving ohlcv:\n %s' % (data,))
        data.drop(columns=['code', 'trade_date'], inplace=True)
        data.set_index(['did', 'sid'], inplace=True)

        for field in self._fields_dict.values():
            single_field_data = data[field.name].unstack()
            single_field_data = single_field_data.sort_index()
            print(single_field_data)
            for sid in single_field_data.columns:
                mmp_obj = self._get_memmap_obj(feild_obj=field, sid=sid)
                mmp_obj[:, sid % self._chunks_s_num] = single_field_data[sid].to_numpy(dtype='int16')

    def _get_memmap_obj(self, feild_obj, sid):
        chunk_id = sid // self._chunks_s_num
        return self._memmap_files_dict[feild_obj][chunk_id]

    def load(self, mode='r+'):
        self._date_index.load()
        self._symbol_index.load()
        self._memmap_files_dict = {}
        sid_len = len(self._symbol_index.codes)
        chunk_shape = (len(self._date_index.dates), self._chunks_s_num)
        chunk_num = sid_len // self._chunks_s_num + 1
        self._memmap_files_dict = {
            field_obj: {sid: np.memmap(os.path.join(self._fields_dir_path[field_obj], f'{sid // self._chunks_s_num}.dat'),
                                       shape=chunk_shape, dtype='int16', mode=mode)
                        for sid in range(chunk_num)}
            for field_obj in self._fields_dir_path.keys()
        }
