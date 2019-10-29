# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-10-29 09:27
"""

from datetime import datetime
import pandas as pd

from ginkgo.core.classical import Classical
from ginkgo.base_calc_manager import BaseCalcManager
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
        self._data_store = []

    def _store_update(self, type_name, data):
        if data:
            self._data_store.append({'metrics': type_name,
                                     'date': self._calc_date,
                                     'market': self._market,
                                     'data': data})

    def calc_3_red_soldiers(self):
        type_name = 'three_red_soldiers'
        try:
            is_red_soldiers_mask = self._calculator_instance.three_red_soldiers()
            symbols = self._data_symbols[is_red_soldiers_mask].to_list()
            self._store_update(type_name, symbols)
        except Exception as e:
            logger.error(e)

    def calc_3_crow(self):
        type_name = 'three_crow'
        try:
            is_three_crow_mask = self._calculator_instance.three_crow()
            symbols = self._data_symbols[is_three_crow_mask].to_list()
            self._store_update(type_name, symbols)
        except Exception as e:
            logger.error(e)

    def calc_multi_cannon(self):
        type_name = 'multi_cannon'
        try:
            is_multi_cannon = self._calculator_instance.multi_cannon()
            symbols = self._data_symbols[is_multi_cannon].to_list()
            self._store_update(type_name, symbols)
        except Exception as e:
            logger.error(e)

    def calc_morning_start(self):
        type_name = 'morning_start'
        try:
            is_morning_start = self._calculator_instance.morning_start()
            symbols = self._data_symbols[is_morning_start].to_list()
            self._store_update(type_name, symbols)
        except Exception as e:
            logger.error(e)

    def calc_duck_head(self):
        type_name = 'duck_head'
        try:
            is_duck_head = self._calculator_instance.duck_head()
            symbols = self._data_symbols[is_duck_head].to_list()
            self._store_update(type_name, symbols)
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
        _open = _open_df.reindex(symbols, axis=1).to_numpy().T
        _high = _high_df.reindex(symbols, axis=1).to_numpy().T
        _low = _low_df.reindex(symbols, axis=1).to_numpy().T
        _close = _close_df.reindex(symbols, axis=1).to_numpy().T
        _volume = _volume_df.reindex(symbols, axis=1).to_numpy().T

        logger.info('calc metrics start')
        self._calculator_instance = Classical(_open, _high, _low, _close, _volume)
        self.calc_3_red_soldiers()
        self.calc_3_crow()
        self.calc_multi_cannon()
        self.calc_morning_start()
        self.calc_duck_head()

    def run(self, start_date=None, end_date=None, symbols=None, market='US', roll=False):
        logger.info(f'running with args end_date: {end_date}, symbols: {symbols}, market: {market}')
        self._end_date = end_date if end_date else datetime.today().date()
        self._start_date = start_date

        if market == 'ALL':
            self.run(end_date, symbols, 'US')
            self.run(end_date, symbols, 'HK')
        else:
            self._market = market
            self._symbols = symbols                 # if symbols else self.load_symbols(market)
            if not roll:
                self.calc_single_market(market)
            else:
                if self._start_date is None:
                    raise ValueError('start_date required when roll is True')
                self.roll_single_market(market)
        # self.save(self._data_store)

    def calc_single_market(self, market='US'):
        self._end_date = self._calc_date = self.get_real_trading_date(self._end_date, bar_count=1, market=market)
        start_date = self.get_real_trading_date(self._end_date, bar_count=self._bar_count, market=market)
        logger.info('loading quote')
        data = self.load_quote(self._symbols, start_date, self._end_date, market=market)
        logger.debug(data.tail())
        self.calc(data)

    def roll_single_market(self, market='US'):
        self._start_date = self.get_real_trading_date(self._start_date, bar_count=1, market=market)
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

        self._winning_probability()

    def _winning_probability(self):
        from collections import defaultdict
        summery_metrics = defaultdict(list)
        winning = defaultdict(lambda: list((0, 0, 0, 0)))
        effect_end_date = self.get_real_trading_date(self._end_date, bar_count=-5, market=self._market)
        for metrics in self._data_store:
            summery_metrics[metrics['date']].append(metrics)

        data = self.load_quote(None, start_date=self._start_date,
                               end_date=effect_end_date, fields=('close', ), market=self._market)

        data.set_index(['timestamp', 'symbol'], inplace=True)
        data.sort_index(inplace=True)
        data = data['close'].unstack()
        logger.debug(f'data: {data.tail()}')
        d1_pct_change = data.pct_change(1).shift(-1) > 0
        d3_pct_change = data.pct_change(3).shift(-3) > 0
        d5_pct_change = data.pct_change(5).shift(-5) > 0

        logger.debug(f'd1_pct_change: {d1_pct_change.tail()}')

        for dt, metrics in summery_metrics.items():
            for m in metrics:
                name = m['metrics']
                symbols = m['data']
                symbols_number = len(symbols)
                try:
                    d1_winning_count = d1_pct_change.loc[dt, symbols].sum()
                    d3_winning_count = d3_pct_change.loc[dt, symbols].sum()
                    d5_winning_count = d5_pct_change.loc[dt, symbols].sum()
                    logger.debug((symbols_number, d1_winning_count, d3_winning_count, d5_winning_count))
                    winning[name][0] += symbols_number
                    winning[name][1] += d1_winning_count
                    winning[name][2] += d3_winning_count
                    winning[name][3] += d5_winning_count

                except KeyError as e:
                    logger.info(e)

        print(winning)

        for k, v in winning.items():
            print(k, v[1] / v[0], v[2] / v[0], v[3]/v[0])