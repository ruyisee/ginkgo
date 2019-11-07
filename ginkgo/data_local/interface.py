# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-11-04 20:17
"""

import abc
import os


class Ingester(abc.ABCMeta):

    @staticmethod
    def ingest_calender(start_date=None, end_date=None, market='CN'):
        raise NotImplementedError

    @staticmethod
    def ingest_daily_quote(start_date, end_date, market='CN'):
        raise NotImplementedError

    @staticmethod
    def ingest_split(start_date, end_date, market='CN'):
        raise NotImplementedError

    @classmethod
    def merge(mcs, other_class):
        for name, method in other_class.__dict__.items():
            if not name.startswith('__'):
                setattr(mcs, name, method)
        return mcs


class LocalDataBase:

    def ingest(self):
        raise NotImplementedError

    def init(self):
        raise NotImplementedError

    def update(self, end_date):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError

    def load(self):
        raise NotImplementedError

    @classmethod
    def check_file(cls, file_abs_path):
        dir_name = os.path.dirname(file_abs_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)


class Index(LocalDataBase):

    def __init__(self, base_path, catgory='stock', market='CN'):
        self._base_path = base_path
        self._catgory = catgory.lower()
        self._index_path = None
        self._market = market.lower()
        self._name_list = None
        self._name_i_map = None
        self._latest_date = None

    def iloc_of(self, name):
        raise NotImplementedError

    def loc_of(self, i):
        raise NotImplementedError