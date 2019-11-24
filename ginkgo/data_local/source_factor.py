# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-11-20 08:24
"""
import os
import sqlite3
from sqlalchemy import create_engine, bindparam, text
import pandas as pd
from ginkgo import PROJECT_CONFIG_DIR
from ginkgo.data_local.interface import LocalDataBase
from ginkgo.data_local.quote_ingester import StandardQuoteIngester
from ginkgo.utils.logger import logger


class AdjFactor(LocalDataBase):

    def __init__(self, base_path, symbol_index, date_index, catgory='stock', market='CN'):
        self._base_path = base_path
        self._catgory = catgory.lower()
        self._market = market.upper()
        self._symbol_index = symbol_index
        self._date_index = date_index
        self.db_path = os.path.join(base_path, self._catgory, self._market)
        self.check_file(self.db_path)
        self.conn = create_engine(f'sqlite:///{self.db_path}/adj_factor.db')
        self._table_name = 'adj_factor'

    def create_index(self):

        sql = f'CREATE UNIQUE INDEX symbol_date on {self._table_name} (symbol, trade_date);'

        csr = self.conn
        csr.execute(sql)

    def ingest(self, symbols, start_date, end_date):
        logger.info('fundamental ingest start')
        if symbols is None:
            symbols = self._symbol_index.symbols
        fetch_chunk_num = 50
        symbols_len = len(symbols)
        all_chunk_num = symbols_len // fetch_chunk_num + 1

        for i in range(0, len(symbols), fetch_chunk_num):
            logger.info(f'ingest split: {i // fetch_chunk_num + 1}/{all_chunk_num}')
            period_symbols = symbols[i: i+fetch_chunk_num]
            yield StandardQuoteIngester.ingest_adj_factors_v(period_symbols, start_date, end_date, self._market)

    def ingest_h(self, symbols, trade_dates):
        return StandardQuoteIngester.ingest_adj_factors_h(symbols, trade_dates, self._market)

    def save(self, data: pd.DataFrame, if_exists='append'):
        logger.info(f'saving data: shape: {data.shape}')
        data.to_sql(self._table_name, self.conn, if_exists=if_exists, index=False)

    def update(self, symbols, end_date):
        factor_latest_date = self.get_latest_date()
        logger.info(f'update adj_factors {factor_latest_date} - {end_date}')

        factor_start_date = self._date_index.offset(factor_latest_date, 3)
        dates = self._date_index.get_calendar(factor_start_date, end_date)
        adj_factor_df = self.ingest_h(None, dates)
        if not adj_factor_df.empty:
            self.save(adj_factor_df[adj_factor_df['trade_date'] > factor_latest_date], 'append')

    def init(self, symbols, start_date, end_date):
        logger.info(f'init adj_factors {start_date} - {end_date}')
        for adj_factor_df in self.ingest(symbols, start_date, end_date):
            if not adj_factor_df.empty:
                self.save(adj_factor_df, 'replace')
        self.create_index()

    def get_latest_date(self):
        sql = f'SELECT MAX(trade_date) FROM {self._table_name}'
        data = self.conn.execute(sql).fetchone()
        return data[0]

    def get_adj_factor(self, symbols, start_date, end_date):
        if symbols is None:
            sql = f'SELECT * FROM {self._table_name} ' \
                f'WHERE trade_date BETWEEN :start_date AND :end_date;'
            params = {'start_date': str(start_date),
                      'end_date': str(end_date)}
        else:
            if isinstance(symbols, str):
                symbols = [symbols, ]
            sql = f'SELECT * FROM {self._table_name} ' \
                f'WHERE symbol IN :symbols AND ' \
                f'trade_date BETWEEN :start_date AND :end_date;'

            params = {'symbols': symbols,
                      'start_date': start_date,
                      'end_date': end_date}

        sql_obj = text(sql)
        if symbols is not None:
            sql_obj = sql_obj.bindparams(bindparam('symbols', expanding=True))

        df = pd.read_sql_query(sql_obj,
                               self.conn,
                               params=params)
        return df

    def do_br(self, fields_arr, calendar, fields_list, symbol):
        start_date = calendar[0]
        end_date = calendar[-1]
        adj_factors = self.get_adj_factor(symbol, start_date, end_date)
        adj_factors = adj_factors.set_index('trade_date')['adj_factor']
        adj_factors = adj_factors.reindex(calendar, method='bfill')
        adj_factors.fillna(value=1.0, inplace=True)
        adj_arr = adj_factors.to_numpy()
        for i, field in enumerate(fields_list):
            if field in ['open', 'high', 'low', 'close']:
                fields_arr[:, i] = fields_arr[:, i] * adj_arr
            elif field == 'volume':
                fields_arr[:, i] = fields_arr[:, i] / adj_arr

        return fields_arr


if __name__ == '__main__':
    symbols = ['000001.SZ', '600547.SH']
    adj_factor = AdjFactor(PROJECT_CONFIG_DIR, None)
    adj_factor.init(symbols, 20180101, 20190101)
    adj_factor.update(symbols, 20190101, 20190801)
    data = adj_factor.get_adj_factor(symbols, 20180101, 20190901)
    print(data)
