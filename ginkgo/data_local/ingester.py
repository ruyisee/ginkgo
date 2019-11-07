# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-11-04 20:17
"""
import os
from ginkgo import USER_CUSTOM_DIR
from ginkgo.data_local.interface import Ingester
from ginkgo.utils.quote_util import QuoteUtil
from ginkgo.utils.logger import logger


INGESTER_FILE = os.path.join(USER_CUSTOM_DIR)


class StandardQuoteIngester(Ingester):

    @staticmethod
    def ingest_calender(start_date=None, end_date=None, market='CN'):
        return QuoteUtil.load_calendar(start_date, end_date, market)

    @staticmethod
    def ingest_symbols(market='CN'):
        return QuoteUtil.load_symbols(market)

    @staticmethod
    def ingest_daily_hists_quote(symbols, start_date, end_date, market='CN'):
        return QuoteUtil.load_daily_hists_quote(symbols, start_date, end_date, market)

    @staticmethod
    def ingest_split(start_date, end_date, market='CN'):
        pass


if os.path.exists(INGESTER_FILE):
    from importlib import import_module
    import sys
    import os
    dir_name = os.path.dirname(INGESTER_FILE)
    module_name = os.path.basename(INGESTER_FILE).split('.')[0]
    sys.path.insert(0, dir_name)
    try:
        custom_module = import_module(module_name)
        StandardQuoteIngester = StandardQuoteIngester.merge(custom_module.CustomQuoteIngester)
    except ImportError:
        logger.warning('custom ingester file name must be %s.py' % module_name)
    except AttributeError:
        logger.warning('custom ingester`s class name must be %s' % 'CustomQuoteIngester')