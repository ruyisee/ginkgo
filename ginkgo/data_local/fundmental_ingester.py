# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-11-21 08:12
"""

from ginkgo.data_local.interface import FundamentalIngester
from


class StandardFundamentalIngester(FundamentalIngester):

    @staticmethod
    def ingest_split(symbols, start_date, end_date, market='CN'):
