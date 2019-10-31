# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-10-29 08:46
"""

from functools import lru_cache
from ginkgo.utils.quote_util import QuoteUtil
from ginkgo.utils.logger import logger


class BaseCalcManager:

    @staticmethod
    def load_quote(symbols, start_date, end_date, market='CN'):
        return QuoteUtil.load_daily_quote(symbols, start_date, end_date, market=market)

    def run(self, roll=False):
        raise NotImplementedError

    def calc(self, data):
        raise NotImplementedError

    @staticmethod
    @lru_cache(4, False)
    def load_calendar(market='CN'):
        return QuoteUtil.load_calendar(market=market)

    def get_real_trading_date(self, dt, bar_count, market='CN'):
        calendar_series = self.load_calendar(market=market)
        try:
            if bar_count > 0:
                return calendar_series[calendar_series <= dt].iloc[-1 * bar_count].to_pydatetime()
            else:
                return calendar_series[calendar_series >= dt].iloc[-1 * bar_count].to_pydatetime()
        except IndexError:
            raise IndexError(f'bar count before {dt} is  less than {bar_count}')

    @staticmethod
    def load_symbols(market='US'):
        return QuoteUtil.load_symbols(market)

    @staticmethod
    def save(data):
        print(data)

    @staticmethod
    def save_winning(data):
        print(data)

    def _winning_probability(self, forecast_data, start_date, end_date, forecast_days=(1, 3, 5), market='US'):
        """
        计算胜率
        :param forecast_data: list[ dict ]
                            [{'metrics': 'three_red_soldiers',
                              'date': datetime.datetime(2019, 9, 27, 0, 0),
                              'market': 'US',
                              'direction': 1,                                               # 预测未来涨跌方向
                              'data': ['HGH', 'LEO', 'EE', 'BBDC', 'NCA', 'USAC', 'MHI']},
                             .....
                            ]
        :param start_date: 计算开始时间
        :param end_date:
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
        summery_metrics = defaultdict(list)
        winning = defaultdict(lambda: defaultdict(list))
        effect_end_date = self.get_real_trading_date(end_date, bar_count=-max(forecast_days), market=market)
        for metrics in forecast_data:
            summery_metrics[metrics['date']].append(metrics)

        data = self.load_quote(None, start_date=start_date,
                               end_date=effect_end_date, fields=('close', ), market=market)

        data.set_index(['timestamp', 'symbol'], inplace=True)
        data.sort_index(inplace=True)
        data = data['close'].unstack()
        logger.debug(f'data: {data.tail()}')

        future_winning_dict = {}
        for d in forecast_days:
            pct_change = data.pct_change(d).shift(-d) > 0
            future_winning_dict[d] = pct_change

        logger.debug(f'd1_pct_change: {future_winning_dict[1].tail()}')

        for dt, metrics in summery_metrics.items():
            for m in metrics:
                name = m['metrics']
                symbols = m['data']
                direction = m['direction']
                symbols_number = len(symbols)
                try:
                    for d, fu in future_winning_dict.items():
                        winning_count = fu.loc[dt, symbols].sum()
                        winning_pct = winning_count / symbols_number
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
