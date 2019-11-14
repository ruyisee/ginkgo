# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-11-14 22:31
"""
import os
from unittest.mock import Mock
import pandas as pd
from ginkgo.core.model import Frame, SFrame
from ginkgo.data_local.data_proxy import DataProxy

class MockDataProxy:
    def __init__(self, market='CN', category='stock'):
        self._daily_quote_df = pd.read_csv(f'./csv/{market.lower()}_daily_{category}_quote.csv')
        self._calendar = self._daily_quote_df[self._daily_quote_df['symbol']=='000001.SZ']['timestamp']

    def get_daily_hist(self, symbol, start_date, end_date, fields_list, br=False):
        this_symbol_df = self._daily_quote_df[self._daily_quote_df['symbol'] == symbol]
        time_period_df = this_symbol_df[(this_symbol_df['timestamp'] >= start_date) & \
                                        (this_symbol_df['timestamp'] <= end_date)]
        frame = Frame(time_period_df[fields_list].to_numpy(), symbol=symbol, index=time_period_df['timestamp'])
        return frame

    def get_daily_hists(self, symbols, start_date, end_date, fields_list, br=False):
        sf = SFrame()
        for symbol in symbols:
            fr = self.get_daily_hist(symbol, start_date, end_date, fields_list, br)
            sf.add(fr)
        return sf

    def get_calendar(self, start_date, end_date):
        return self._calendar[(self._calendar >= start_date) & (self._calendar <= end_date)].to_list()

    def get_date_offset(self, start_date, bar_count):
        if bar_count >= 0:
            try:
                dt = self._calendar[self._calendar <= start_date].iloc[-bar_count]
            except KeyError:
                dt = self._calendar[0]
        else:
            try:
                dt = self._calendar[self._calendar >= start_date].iloc[-bar_count]
            except KeyError:
                dt = self._calendar[-1]

    def get_vaild_date(self, name):
        return self.get_date_offset(name, bar_count=0)


def mock_data_proxy():
    DataProxy = Mock()
    mdp = MockDataProxy()
    DataProxy.get_daily_hist = mdp.get_daily_hist
    DataProxy.get_daily_hists = mdp.get_daily_hists
    DataProxy.get_calendar = mdp.get_calendar
    DataProxy.get_date_offset = mdp.get_date_offset
    DataProxy.get_split = None
    DataProxy.get_symbols = None
    DataProxy.get_valid_date =
