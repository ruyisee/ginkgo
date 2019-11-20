# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-11-20 08:24
"""
import os
from ginkgo.data_local.interface import LocalDataBase


class Fundamental(LocalDataBase):

    def __init__(self, base_path, catgory='stock', market='CN'):
        self._base_path = base_path
        self._catgory = catgory.lower()
        self._market = market.upper()
        self.db_path = os.path.join(base_path, self._catgory, self._market)

    def get_split(self, symbols, start_date, end_date):
        pass
