# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-11-10 16:38
"""

from datetime import datetime


def datetime_to_int(dt, l=8):
    if l == 8:
        return int(datetime.strftime(dt, '%Y%m%d'))
