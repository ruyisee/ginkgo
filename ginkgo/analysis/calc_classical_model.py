# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-10-29 09:27
"""
import pandas as pd
import numpy as np
from ginkgo.core.classical_form import Classical
from ginkgo.utils.logger import logger
from datetime import datetime
from ginkgo.core.analysis_util import remove_cent
from ginkgo.constant import Market
from ginkgo.analysis.base_calc_manager import BaseCalcManager
from ginkgo.data_local.data_proxy import


class ClassicalFormManager(BaseCalcManager):

    def __init__(self, bar_count=90):
        self._start_date = None
        self._end_date = None
        self._calc_date = None
        self._symbols = None
        self._market = None
        self._bar_count = bar_count
        self._data_symbols = None
        self._datetime_index = None
        self._data_store = None
        self._calculator_instance = None
        self._store_init()

    def _store_init(self):
        self._data_store = []

    def _store_update(self, type_name, symbols, extra):
        self._data_store.append({
            'metrics': type_name,
            'symbols': symbols,
            'extra': extra
        })

    def call_funcs(self):
        for func_name in dir(self._calculator_instance):
            if not func_name.startswith('_'):
                func = getattr(self._calculator_instance, func_name)
                symbols, form_dates = func()
                self._store_update(func_name, symbols, form_dates)

    def calc(self, data):
        logger.info('cleaning invalid data')
        data.set_index(['timestamp', 'symbol'], inplace=True)
        data.sort_index(inplace=True)
        _open_df = data['open'].unstack().fillna(method='pad').fillna(value=0)
        _high_df = data['high'].unstack().fillna(method='pad').fillna(value=0)
        _low_df = data['low'].unstack().fillna(method='pad').fillna(value=0)
        _close_df = data['close'].unstack().fillna(method='pad').fillna(value=0)
        _volume_df = data['volume'].unstack().fillna(method='pad').fillna(value=0)

        symbols = set(_open_df.columns)
        symbols.intersection_update(set(_high_df.columns))
        symbols.intersection_update(set(_low_df.columns))
        symbols.intersection_update(set(_close_df.columns))
        symbols.intersection_update(set(_volume_df.columns))
        symbols = list(symbols)
        symbols_len_bf_rm = len(symbols)
        symbols = remove_cent(close_arr=_close_df[symbols].to_numpy(),
                              volume_arr=_volume_df[symbols].to_numpy(), symbols=symbols)
        symbols = set(symbols)
        symbols_len_af_rm = len(symbols)
        logger.info(f'removed cent symbol count from {symbols_len_bf_rm} to {symbols_len_af_rm}')

        self._data_symbols = pd.Index(symbols)
        self._datetime_index = pd.to_datetime(_open_df.index)
        _date_index_str = np.array([int(datetime.strftime(d, '%Y%m%d')) for d in self._datetime_index])
        _open = _open_df.reindex(symbols, axis=1).to_numpy()
        _high = _high_df.reindex(symbols, axis=1).to_numpy()
        _low = _low_df.reindex(symbols, axis=1).to_numpy()
        _close = _close_df.reindex(symbols, axis=1).to_numpy()
        _volume = _volume_df.reindex(symbols, axis=1).to_numpy()

        logger.info(f'calc metrics start, open shape: {_open.shape}')
        self._calculator_instance = Classical(_open, _high, _low, _close, _volume, np.array(list(symbols)),
                                              date_index_arr=_date_index_str[-60:])
        self.call_funcs()

    def run(self, start_date=None, end_date=None, symbols=None, market=Market.US, roll=False):
        logger.info(f'running with args end_date: {end_date}, symbols: {symbols}, market: {market}')
        self._end_date = end_date if end_date else datetime.today().date()
        self._start_date = start_date

        if market == Market.ALL:
            self.run(start_date, end_date, symbols, Market.US, roll)
            self.run(start_date, end_date, symbols, Market.HK, roll)
        else:
            self._market = market
            self._symbols = symbols                 # if symbols else self.load_symbols(market)
            if not roll:
                self.calc_single_market(market)
            else:
                if self._start_date is None:
                    raise ValueError('start_date required when roll is True')
                self.calc_single_market_roll(market)

    def calc_single_market(self, market=Market.US):
        self._end_date = self.get_real_trading_date(self._end_date, bar_count=1, market=market)
        start_date = self.get_real_trading_date(self._end_date, bar_count=self._bar_count, market=market)
        self._calc_date = self._end_date
        data = self.load_quote(self._symbols, start_date, self._end_date, market=market)
        logger.debug(data.tail())
        self.calc(data)
        self.save(self._data_store)

    def calc_single_market_roll(self, market=Market.US):
        self._start_date = self.get_real_trading_date(self._start_date, bar_count=self._bar_count, market=market)
        self._end_date = self.get_real_trading_date(self._end_date, bar_count=1, market=market)

        data_start_date = self.get_real_trading_date(self._start_date, bar_count=self._bar_count, market=market)
        logger.info('loading quote')

        data = self.load_quote(self._symbols, data_start_date, self._end_date, market=market)

        calendar = self.load_calendar(market)
        calendar = calendar[(calendar <= self._end_date) & (calendar >= self._start_date)]

        for dt in calendar:
            period_start_date = self.get_real_trading_date(dt, self._bar_count, market)
            period_data = data[(data['timestamp'] <= dt) & (data['timestamp'] >= period_start_date)]
            self._calc_date = dt.to_pydatetime()
            self.calc(period_data)
        self.save(self._data_store)

    @staticmethod
    def save(data):
        print(data)
