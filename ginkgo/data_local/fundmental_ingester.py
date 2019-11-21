# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-11-21 08:12
"""
import os
from ginkgo import USER_CUSTOM_DIR
from ginkgo.utils.logger import logger
from ginkgo.data_local.interface import FundamentalIngester
from ginkgo.utils.fundamental_util import FundmentalUtil


class StandardFundamentalIngester(FundamentalIngester):

    @staticmethod
    def ingest_split(symbols, start_date, end_date, market='CN'):
        return FundmentalUtil.load_split(symbols, start_date, end_date, market)


if os.path.exists(INGESTER_FILE):
    from importlib import import_module
    import sys
    import os
    dir_name = os.path.dirname(INGESTER_FILE)
    module_name = os.path.basename(INGESTER_FILE).split('.')[0]
    sys.path.insert(0, dir_name)
    try:
        custom_module = import_module(module_name)
        StandardFundamentalIngester = StandardFundamentalIngester.merge(custom_module.CustomFundamentalIngester)
    except ImportError:
        logger.warning('custom ingester file name must be %s.py' % module_name)
    except AttributeError:
        logger.warning('custom ingester`s class name must be %s' % 'CustomFundamentalIngester')
