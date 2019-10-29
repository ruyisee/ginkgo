# -*- coding:utf-8 -*-
"""
@author: kangyuqiang

@since: 2019-10-29 08:29
"""

import logging
import sys

LOG_FORMAT = logging.Formatter('%(asctime)s %(levelname)s %(module)s.%(funcName)s %(message)s ')

handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(LOG_FORMAT)
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)