# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-11-15 09:58
"""
import pytest
from ginkgo.data_local.data_proxy import DataProxy
from ginkgo.core.analysis_util import zigzag

from tests.mock.mock_data_proxy import mock_data_proxy


class TestCommon:

    @pytest.fixture('class')
    def setup_data(self):
        mock_data_proxy()

    def test_zigzag():
        pass
