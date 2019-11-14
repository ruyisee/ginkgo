# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-10-29 08:46
"""

from functools import lru_cache
from prettyprinter import cpprint
from ginkgo.utils.logger import logger
from ginkgo.analysis.local_client import get_local_client


class BaseCalcManager:

    @staticmethod
    def get_daily_hists(symbols, start_date, end_date, fields=('open', 'low', 'high', 'close', 'volume'), market='CN'):
        client = get_local_client(market=market)
        sframe = client.get_daily_hists(symbols, start_date, end_date, fields_list=fields)
        return sframe.to_dataframe()

    def run(self, winning=False):
        raise NotImplementedError

    def calc(self, data):
        raise NotImplementedError

    @staticmethod
    @lru_cache(4, False)
    def get_calendar(start_date, end_date, market='CN'):
        client = get_local_client(market=market)
        return client.get_calendar(start_date, end_date)

    def get_date_offset(self, dt, bar_count, market='US'):
        client = get_local_client(market=market)
        return client.get_date_offset(dt, bar_count)

    @staticmethod
    def get_symbols(market='CN', industry=None, area=None, board=None):
        client = get_local_client(market=market)
        constracts = client.get_symbols(industry, area, board)
        # return ['000710']
        return [const.symbol for const in constracts]

    @staticmethod
    def get_valid_date(dt, market='CN'):
        client = get_local_client(market=market)
        return client.get_valid_date(dt)

    @staticmethod
    def save(data):
        cpprint(data)

    def _winning_probability(self, forecast_data, forecast_days=(1, 3, 5), quote_data=None, market='US'):
        """
        计算胜率
        :param forecast_data: ditc[ list ]
                            { datetime.datetime(2019, 9, 27, 0, 0):
                                  [{'metrics': 'three_red_soldiers',
                                    'date': datetime.datetime(2019, 9, 27, 0, 0),
                                    'market': 'US',
                                    'direction': 1,                                               # 预测未来涨跌方向
                                    'data': ['HGH', 'LEO', 'EE', 'BBDC', 'NCA', 'USAC', 'MHI']},
                                    ....
                                   ],
                             .....
                            }
        :param forecast_days:
                            需要检验的未来天数列表， (1, 3, 5)
        :param market:
        :return: dict
                 {'three_red_soldiers':  {1: 0.49767227902371464,
                                          3: 0.43380883095574463,
                                          5: 0.4075340831245499},
                   'three_crow':  {1: 0.563627227684226,
                                   3: 0.5850837879834898,
                                   5: 0.5889460044487472},
                  ......
                 }
        """
        from collections import defaultdict

        winning = defaultdict(lambda: defaultdict(list))

        start_date = min(forecast_data.keys())
        end_date = max(forecast_data.keys())

        if quote_data is None:
            effect_end_date = self.get_date_offset(end_date, bar_count=-max(forecast_days), market=market)
            quote_data = self.get_daily_hists(None, start_date=start_date,
                                              end_date=effect_end_date, fields=('close', ), market=market)

        quote_data.set_index(['timestamp', 'symbol'], inplace=True)
        quote_data.sort_index(inplace=True)
        quote_data = quote_data['close'].unstack()
        logger.debug(f'data: {quote_data.tail()}')

        future_winning_dict = {}
        for d in forecast_days:
            pct_change = quote_data.pct_change(d).shift(-d)
            pct_change.dropna(how='all', inplace=True)
            future_winning_dict[d] = pct_change > 0

        logger.debug(f'd1_pct_change: {future_winning_dict[1].tail()}')

        for dt, metrics in forecast_data.items():

            for m in metrics:
                name = m['metrics']
                symbols = m['data']
                direction = m['direction']
                symbols_number = len(symbols)
                try:
                    for d, fu in future_winning_dict.items():
                        try:
                            winning_count = fu.loc[dt, symbols].sum()
                        except KeyError:
                            logger.debug(f'winning at {dt} con`t calc for quote is less {max(forecast_days)} after')
                            continue
                        winning_pct = int(winning_count / symbols_number)
                        if direction == -1:
                            winning_pct = 1 - winning_pct
                        winning[name][d].append(winning_pct)

                except KeyError as e:
                    logger.info(e)

        for k, v in winning.items():
            for d, pct in v.items():
                win_avg_pct = sum(pct) / len(pct)
                winning[k][d] = win_avg_pct
        return winning