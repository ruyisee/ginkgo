# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-11-04 19:18
"""

import os
import pickle
from ginkgo.data_local.ingester import StandardQuoteIngester
from ginkgo.data_local.interface import Index
from ginkgo.utils.logger import logger


class RowDateIndex(Index):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._index_path = \
            os.path.join(self._base_path, f'meta/row_date_index.plk')
        self.check_file(self._index_path)

    def ingest(self, start_date=None, end_date=None):
        logger.info(f'ingest calendar from {start_date} to {end_date}')
        return StandardQuoteIngester.ingest_calender(start_date, end_date, self._market)

    def init(self, start_date, end_date):
        logger.info(f'init date index {start_date} - {end_date}')
        calendar_list = self.ingest(start_date, end_date)
        self.save(calendar_list)
        self.load()

    def update(self, end_date):
        self.load()
        logger.info('updating date index')
        old_latest_date = self._latest_date
        if self._latest_date < end_date:
            logger.info(f'updating date {self._latest_date} - {end_date}')
            calendar_list = self.ingest(self._latest_date, end_date)
            len_count = len(self._name_list)
            for date_str in calendar_list:
                if date_str not in self._name_i_map:
                    self._name_list.append(date_str)
                    self._name_i_map[date_str] = len_count
                    len_count += 1
            self.save(self._name_list)
            self.load()
            return old_latest_date
        else:
            logger.info('date no need to update')
            return None

    def load(self):
        logger.info('loading date info')
        with open(self._index_path, mode='rb+') as f:
            self._name_list = pickle.load(f)
        self._name_i_map = {}
        for i, name in enumerate(self._name_list):
            self._name_i_map[name] = i
        self._latest_date = self._name_list[-1]

    def save(self, data):
        logger.info('saving date index')
        with open(self._index_path, 'wb+') as f:
            pickle.dump(data, f)

    def i_of(self, name):
        name = int(name)
        if (name < self._name_list[0]) or (name > self._name_list[-1]):
            raise ValueError(f'date {name} out of {self._name_list[0]} - {self._name_list[-1]}')
        while True:
            try:
                i = self._name_i_map[name]
                break
            except KeyError:
                name -= 1

        return i

    def o_of(self, i):
        return self._name_list[i]

    def get_calendar(self, start_date, end_date):
        start_id = self.i_of(start_date) if start_date else None
        end_id = self.i_of(end_date) + 1 if end_date else None
        return self._name_list[start_id: end_id]

    @property
    def dates(self):
        return self._name_list

    def offset(self, start_date, bar_cunt):
        start_id = self.i_of(start_date)
        offset_id = start_id - bar_cunt
        if offset_id < 0:
            logger.warning('date offset out of range start')
            offset_id = 0
        elif offset_id > len(self.dates) - 1:
            offset_id = -1
        return self.o_of(offset_id)
