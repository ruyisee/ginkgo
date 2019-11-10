# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-11-10 08:57
"""
import logging

import click

from ginkgo.__main__ import cli
from ginkgo import COMMANDS_LIST
from ginkgo.analysis.calc_classical_model import ClassicalModelManager
from ginkgo.utils.logger import logger


@cli.command()
@click.help_option('-h', '--help')
@click.option('-m', '--market', default='CN', help='市场, ALL, US, HK')
@click.option('-b', '--bar_count', default=None, help='向前取多少天的数据')
@click.option('-wp', '--winning_period', default=60, help='向前取多少天的数据')
@click.option('-ed', '--end_date', default=None, callback=lambda _, x: int(x))
@click.option('-s', '--symbols', default=None, callback=lambda _, x: x.split(',') if x else None)
@click.option('-fd', '--forecast_days', default=None, callback=lambda _, x: x.split(',') if x else None)
@click.option('-d', '--debug', is_flag=True)
@click.option('-w', '--winning', is_flag=True)
@click.pass_context
def calc_classical(ctx, bar_count, market, winning_period, forecast_days, end_date, symbols, debug, winning):
    if forecast_days:
        forecast_days = [int(x) for x in forecast_days]
    if debug:
        logger.setLevel(logging.DEBUG)
    m = ClassicalModelManager(bar_count=bar_count)
    m.run(end_date=end_date, symbols=symbols, market=market, forecast_days=forecast_days,
          winning_period=winning_period, winning=winning)


COMMANDS_LIST.append(calc_classical)