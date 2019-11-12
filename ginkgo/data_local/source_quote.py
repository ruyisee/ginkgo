# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-11-07 10:14
"""
import os
import numpy as np
from collections import defaultdict

from ginkgo.core.model import Frame, SFrame
from ginkgo.data_local.source_date_index import RowDateIndex
from ginkgo.data_local.source_symbol_index import ColSymbolIndex
from ginkgo.data_local.ingester import StandardQuoteIngester
from ginkgo.data_local.interface import LocalDataBase
from ginkgo.data_local.fields import fields_manager, fields_dict
from ginkgo.utils.logger import logger


class QuoteModel(LocalDataBase):

    def __init__(self, base_path, fields_dict=fields_dict,
                 chunks_s_num=300, catgory='stock', freq='daily', market='CN'):

        self._base_path = os.path.join(base_path, f'{catgory.lower()}/{market.lower()}/{freq.lower()}')
        self._market = market
        self._fields_dict = fields_dict
        self._date_index = RowDateIndex(self._base_path, catgory=catgory, market=market)
        self._chunks_s_num = chunks_s_num
        self._symbol_index = ColSymbolIndex(self._base_path, chunks_s_num=chunks_s_num, catgory=catgory, market=market)
        self._fields_dir_path = \
            {field: os.path.join(self._base_path, f'{field.name}') for field in self._fields_dict.values()}
        self._check_dir(self._fields_dir_path.values())
        self._memmap_files_dict = defaultdict(dict)

        # method proxy
        self.get_calendar = self._date_index.get_calendar
        self.contracts_filter = self._symbol_index.contracts_filter
        self.get_date_offset = self._date_index.offset
        self.get_valid_date = self._date_index.get_valid_date

    def _check_dir(self, dirs):
        for d in dirs:
            self.check_file(d, is_dir=True)

    def ingest(self, symbols, start_date, end_date):
        logger.info(f'quote ingest start')

        if symbols is None:
            symbols = self._symbol_index.symbols

        fetch_chunk_num = 50
        symbols_len = len(symbols)
        all_chunk_num = symbols_len // fetch_chunk_num + 1

        for i in range(0, len(symbols), fetch_chunk_num):
            logger.info(f'ingest quote: {i // fetch_chunk_num + 1}/{all_chunk_num}')
            period_symbols = symbols[i: i+fetch_chunk_num]
            yield StandardQuoteIngester.ingest_daily_hists_v(period_symbols, start_date, end_date)

    def ingest_h(self, symbols, trade_dates):
        logger.info(f'quote ingest start')
        return StandardQuoteIngester.ingest_daily_hists_h(symbols, trade_dates, self._market)

    def init(self, symbols, start_date, end_date):
        self._date_index.init(start_date, end_date)
        self._symbol_index.init()
        self.load(mode='w+')
        for quote in self.ingest(symbols, start_date, end_date):
            if not quote.empty:
                self.save(quote)

    def update(self, end_date, start_date=None, symbols=None, f=False):
        self._symbol_index.update()
        logger.info('updating quote')
        old_latest_date = self._date_index.update(end_date)
        if (old_latest_date is None) and (start_date is None):
            logger.info('quote no need to update')
            return
        elif start_date is not None:
            if old_latest_date is not None:
                if not f:
                    start_date = min(start_date, old_latest_date + 1)
                    logger.info(f'quote updating append {start_date} - {end_date}')
                else:
                    start_date = old_latest_date + 1
                    logger.info(f'quote updating in situ {start_date} - {end_date}')
            trade_dates = self._date_index.get_calendar(start_date, end_date)
            data = self.ingest_h(symbols=symbols, trade_dates=trade_dates)
        else:
            logger.info(f'quote updating append {old_latest_date + 1} - {end_date}')
            trade_dates = self._date_index.get_calendar(old_latest_date+1, end_date)
            data = self.ingest_h(symbols=symbols, trade_dates=trade_dates)
        self.load('r+')
        if not data.empty:
            self.save(data)

    def save(self, data):
        data['sid'] = sids = data.symbol.apply(self._symbol_index.i_of)
        data['did'] = data.trade_date.apply(self._date_index.i_of)
        logger.debug('[daily_bar_util] saving ohlcv:\n %s' % (data,))
        data['did'] = data['did'].astype('int')
        data['sid'] = data['sid'].astype('int')
        did_calendar = list(range(min(data['did']), max(data['did'])+1))
        data.set_index(['did', 'sid'], inplace=True)
        start_id = did_calendar[0]
        end_id = did_calendar[-1]
        for field in self._fields_dict.values():
            single_field_data = data[field.name].unstack()
            single_field_data = single_field_data.sort_index().fillna(0)
            single_field_data = single_field_data.reindex(did_calendar, method='pad')
            for sid in single_field_data.columns:
                mmp_obj = self._get_memmap_obj(feild_obj=field, sid=sid)
                mmp_obj[start_id:end_id+1, sid % self._chunks_s_num] = \
                    (single_field_data[sid] * field.precision).to_numpy(dtype='int32')

    def _get_memmap_obj(self, feild_obj, sid):
        chunk_id = sid // self._chunks_s_num
        return self._memmap_files_dict[feild_obj][chunk_id]

    def load(self, mode='r+'):
        self._date_index.load()
        self._symbol_index.load()
        self._memmap_files_dict = defaultdict(dict)
        sid_len = len(self._symbol_index.symbols)
        chunk_shape = (len(self._date_index.dates), self._chunks_s_num)
        chunk_num = sid_len // self._chunks_s_num + 1

        ### init memmap
        for field, path in self._fields_dir_path.items():
            for chunk_id in range(chunk_num):
                self._memmap_files_dict[field][chunk_id] = \
                np.memmap(os.path.join(path, f'{chunk_id}.dat'),
                          shape=chunk_shape, dtype='int32', mode=mode)

    def fields_to_obj(self, fields_list):
        return [self._fields_dict[field_name] for field_name in fields_list]

    def get_symbol_data(self, symbol, start_date, end_date, fields_list=None):
        if fields_list is None:
            fields_list = list(self._fields_dict.keys())
        sid = self._symbol_index.i_of(symbol, error='raise')
        calendar = self._date_index.get_calendar(start_date, end_date)
        start_id = self._date_index.i_of(start_date)
        end_id = self._date_index.i_of(end_date)
        chunk_sid = sid % self._chunks_s_num

        fields_arr_list = []
        for field_obj in self.fields_to_obj(fields_list):
            mmp_obj = self._get_memmap_obj(feild_obj=field_obj, sid=sid)
            arr = mmp_obj[start_id:end_id+1, chunk_sid] / field_obj.precision
            fields_arr_list.append(arr)

        fields_arr = np.array(fields_arr_list).T
        frame = Frame(fields_arr, calendar, fields_list, symbol)
        return frame

    def get_symbols_data(self, symbols, start_date, end_date, fields_list=None):
        if isinstance(symbols, str):
            symbols = [symbols, ]
        if fields_list is None:
            fields_list = list(self._fields_dict.keys())
        sf = SFrame()
        for symbol in symbols:
            frame = self.get_symbol_data(symbol, start_date, end_date, fields_list)
            sf.add(frame)

        return sf
