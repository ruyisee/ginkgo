# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-10-29 08:30
"""

import logging
import click
from ginkgo.utils.logger import logger
from ginkgo import COMMANDS_LIST
from ginkgo.analysis.calc_classical_model import ClassicalModelManager


@click.group()
@click.help_option('-h', '--help')
@click.pass_context
def cli(ctx):
    pass


@cli.command()
@click.help_option('-h', '--help')
@click.option('-m', '--market', default='US', help='市场, ALL, US, HK')
@click.option('-b', '--bar_count', default=None, help='向前取多少天的数据')
@click.option('-wp', '--winning_period', default=60, help='向前取多少天的数据')
@click.option('-ed', '--end_date', default=None)
@click.option('-s', '--symbols', default=None, callback=lambda _, x: x.split(',') if x else None)
@click.option('-fd', '--forecast_days', default=None, callback=lambda _, x: x.split(',') if x else None)
@click.option('-d', '--debug', is_flag=True)
@click.option('-w', '--winning', is_flag=True)
def calc_classic(ctx, bar_count, market, winning_period, forecast_days, end_date, symbols, debug, winning):
    if forecast_days:
        forecast_days = [int(x) for x in forecast_days]
    if debug:
        logger.setLevel(logging.DEBUG)
    m = ClassicalModelManager(bar_count=bar_count)
    m.run(end_date=end_date, symbols=symbols, market=market, forecast_days=forecast_days,
          winning_period=winning_period, winning=winning)


def load_command():
    for command in COMMANDS_LIST:
        cli.add_command(command)


if __name__ == '__main__':
    from ginkgo.data_local.__main__ import *
    load_command()
    cli()