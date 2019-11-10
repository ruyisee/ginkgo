# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-11-09 20:52
"""

from ginkgo.data_local.data_proxy import DataProxy

LOCAL_CLIENT_LIST = {}


def get_local_client(catgory='stock', market='CN'):
    key = f'{catgory}-{market.upper()}'
    if not LOCAL_CLIENT_LIST.get(key, None):
        client = DataProxy(catgory=catgory, market=market.upper())
        LOCAL_CLIENT_LIST[key] = client
    return LOCAL_CLIENT_LIST[key]
