# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-10-29 10:31
"""
import os
from ginkgo.config import load_config
from ginkgo.config import PROJECT_CONFIG_DIR

conf = load_config()

USER_CUSTOM_DIR = os.path.join(PROJECT_CONFIG_DIR, 'custom')