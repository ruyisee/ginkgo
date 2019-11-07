# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-11-07 09:20
"""


class BaseContract:
    pass


class StockContract(BaseContract):

    __slots__ = ['code', 'symbol', 'name', 'market', 'industry', 'board',
                 'list_date', 'lot_size', 'sid', 'area']

    def __init__(self, code, sid, symbol, name, market, industry, board, area=None, list_date=None, lot_size=1):
        self.code = code
        self.symbol = symbol
        self.name = name
        self.market = market
        self.industry = industry
        self.board = board
        self.area = area
        self.list_date = list_date
        self.lot_size = lot_size
        self.sid = sid
