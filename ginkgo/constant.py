# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019/12/25 8:10 PM
"""


class EnumType:
    pass


class Direction(EnumType):
    LONG = 1
    SHORT = -1


class Market(EnumType):
    US = 'US'
    HK = 'HK'
    CN = 'CN'
