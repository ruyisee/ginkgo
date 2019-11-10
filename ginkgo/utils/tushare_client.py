# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-10-30 09:29
"""
import tushare

from ginkgo import conf

tushare.set_token(conf['tushare']['token'])

ts_pro = tushare.pro_api()
