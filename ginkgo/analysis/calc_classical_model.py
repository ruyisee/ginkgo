# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-10-29 09:27
"""
from collections import defaultdict
from datetime import datetime, timedelta
import pandas as pd

from ginkgo.core.classical import Classical
from ginkgo.analysis.base_calc_manager import BaseCalcManager
from ginkgo.utils.logger import logger


class ClassicalModelManager(BaseCalcManager):

    def __init__(self, bar_count=5):
        self._start_date = None
        self._end_date = None
        self._calc_date = None
        self._symbols = None
        self._market = None
        self._bar_count = bar_count if bar_count else 80
        self._data_symbols = None
        self._datetime_index = None
        self._data_store = None
        self._calculator_instance = None
        self._store_init()

    def _store_init(self):
        self._data_store = defaultdict(list)

    def _store_update(self, type_name, data, direction=1):
        if data:
            self._data_store[self._calc_date].append({'metrics': type_name,
                                                      'date': self._calc_date,
                                                      'market': self._market,
                                                      'direction': direction,
                                                      'data': data})

    def _c_three_red_soldiers(self):
        type_name = 'three_red_soldiers'
        try:
            mask = self._calculator_instance.three_red_soldiers()
            symbols = self._data_symbols[mask].to_list()
            self._store_update(type_name, symbols, direction=1)
        except Exception as e:
            logger.error(e)

    def _c_three_crow(self):
        type_name = 'three_crow'
        try:
            mask = self._calculator_instance.three_crow()
            symbols = self._data_symbols[mask].to_list()
            self._store_update(type_name, symbols, direction=-1)
        except Exception as e:
            logger.error(e)

    def _c_multi_cannon(self):
        type_name = 'multi_cannon'
        try:
            mask = self._calculator_instance.multi_cannon()
            symbols = self._data_symbols[mask].to_list()
            self._store_update(type_name, symbols, direction=1)
        except Exception as e:
            logger.error(e)

    def _c_morning_start(self):
        type_name = 'morning_start'
        try:
            mask = self._calculator_instance.morning_start()
            symbols = self._data_symbols[mask].to_list()
            self._store_update(type_name, symbols, direction=1)
        except Exception as e:
            logger.error(e)

    def _c_duck_head(self):
        type_name = 'duck_head'
        try:
            mask = self._calculator_instance.duck_head()
            symbols = self._data_symbols[mask].to_list()
            self._store_update(type_name, symbols, direction=1)
        except Exception as e:
            logger.error(e)

    def _c_rise_wrap_fall(self):
        type_name = 'rise_wrap_fall'
        try:
            mask = self._calculator_instance.rise_wrap_fall()
            symbols = self._data_symbols[mask].to_list()
            self._store_update(type_name, symbols, direction=1)
        except Exception as e:
            logger.error(e)

    def _c_fall_wrap_raise(self):
        type_name = 'fall_wrap_raise'
        try:
            mask = self._calculator_instance.fall_wrap_raise()
            symbols = self._data_symbols[mask].to_list()
            self._store_update(type_name, symbols, direction=-1)
        except Exception as e:
            logger.error(e)

    def _c_rise_pregnant(self):
        type_name = 'rise_pregnant'
        try:
            mask = self._calculator_instance.rise_pregnant_line()
            symbols = self._data_symbols[mask].to_list()
            self._store_update(type_name, symbols, direction=1)
        except Exception as e:
            logger.error(e)

    def _c_golden_spider(self):
        type_name = 'golden_spider'
        try:
            mask = self._calculator_instance.golden_spider()
            symbols = self._data_symbols[mask].to_list()
            self._store_update(type_name, symbols, direction=1)
        except Exception as e:
            logger.error(e)

    def _c_dead_spider(self):
        type_name = 'dead_spider'
        try:
            mask = self._calculator_instance.dead_spider()
            symbols = self._data_symbols[mask].to_list()
            self._store_update(type_name, symbols, direction=-1)
        except Exception as e:
            logger.error(e)

    def calc(self, data):
        logger.info('cleaning invalid data')
        data.set_index(['timestamp', 'symbol'], inplace=True)
        _open_df = data['open'].unstack().dropna(axis=1, how='any')
        _high_df = data['high'].unstack().dropna(axis=1, how='any')
        _low_df = data['low'].unstack().dropna(axis=1, how='any')
        _close_df = data['close'].unstack().dropna(axis=1, how='any')
        _volume_df = data['volume'].unstack().dropna(axis=1, how='any')

        symbols = set(_open_df.columns)
        symbols.intersection_update(set(_high_df.columns))
        symbols.intersection_update(set(_low_df.columns))
        symbols.intersection_update(set(_close_df.columns))
        symbols.intersection_update(set(_volume_df.columns))
        symbols = list(symbols)
        self._data_symbols = pd.Index(symbols)
        self._datetime_index = pd.to_datetime(_open_df.index)
        _open = _open_df.reindex(symbols, axis=1).to_numpy()
        _high = _high_df.reindex(symbols, axis=1).to_numpy()
        _low = _low_df.reindex(symbols, axis=1).to_numpy()
        _close = _close_df.reindex(symbols, axis=1).to_numpy()
        _volume = _volume_df.reindex(symbols, axis=1).to_numpy()

        logger.info(f'calc metrics start, open shape: {_open.shape}')
        self._calculator_instance = Classical(_open, _high, _low, _close, _volume)
        self._c_three_red_soldiers()
        self._c_three_crow()
        self._c_multi_cannon()
        self._c_morning_start()
        self._c_duck_head()
        self._c_rise_wrap_fall()
        self._c_fall_wrap_raise()
        self._c_rise_pregnant()
        self._c_golden_spider()
        self._c_dead_spider()

    def run(self, end_date=None, symbols=None, market='US', winning_period=60, forecast_days=(1, 3, 5), winning=False):
        logger.info(f'running with args end_date: {end_date}, symbols: {symbols}, market: {market}')
        self._end_date = end_date if end_date else int((datetime.today().date() - timedelta(days=1)).strftime('%Y%m%d'))
        # self._start_date = start_date

        if market == 'ALL':
            self.run(end_date, symbols, 'CN')
        else:
            self._market = market
            self._symbols = symbols                 # if symbols else self.load_symbols(market)
            if not winning:
                self.calc_single_market(market)
            else:
                # if self._start_date is None:
                #     raise ValueError('start_date required when roll is True')
                self.calc_single_market_with_winning(winning_period, market)

    def calc_single_market(self, market='US'):
        if self._symbols is None:
            self._symbols = self.get_symbols(market)
        self._end_date = self._calc_date = self.get_valid_date(self._end_date)
        start_date = self.get_date_offset(self._end_date, bar_count=self._bar_count, market=market)
        logger.info('loading quote')
        data = self.get_daily_hists(self._symbols, start_date, self._end_date, market=market)
        logger.debug(data.tail())
        self.calc(data)
        self.save(list(self._data_store[self._end_date]))

    def calc_single_market_with_winning(self, winning_period, market='US'):
        if self._symbols is None:
            self._symbols = self.get_symbols(market)
        self._start_date = self.get_date_offset(self._end_date, bar_count=winning_period, market=market)
        self._end_date = self.get_date_offset(self._end_date, bar_count=1, market=market)

        data_start_date = self.get_date_offset(self._start_date, bar_count=self._bar_count, market=market)
        logger.info('loading quote')

        data = self.get_daily_hists(self._symbols, data_start_date, self._end_date, market=market)
        calendar = self.get_calendar(start_date=self._start_date, end_date=self._end_date, market=market)

        for dt in calendar:
            period_start_date = self.get_date_offset(dt, self._bar_count, market)
            period_data = data[(data['timestamp'] <= dt) & (data['timestamp'] >= period_start_date)]
            self._calc_date = dt
            self.calc(period_data)

        logger.info('calc winning probability')

        winning_data = self._winning_probability(self._data_store, quote_data=data, market=self._market)

        data_store = self._data_store[self._end_date]

        for d in data_store:
            metrics = d['metrics']
            d['winning'] = winning_data[metrics]

        self.save(data_store)

