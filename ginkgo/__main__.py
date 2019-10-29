# -*- coding:utf-8 -*-
"""
@author: kangyuqiang

@since: 2019-10-29 08:30
"""

import logging
import click
from ginkgo.utils.logger import logger
from ginkgo.analysis.calc_classical_model import ClassicalModelManager


@click.group()
def cli():
    pass


@cli.command()
@click.help_option('-h', '--help')
@click.option('-m', '--market', default='CN', help='市场, ALL, US, HK')
@click.option('-b', '--bar_count', default=None, help='向前取多少天的数据')
@click.option('-st', '--start_date', default=None)
@click.option('-ed', '--end_date', default=None)
@click.option('-s', '--symbols', default=None, callback=lambda _, x: x.split(',') if x else None)
@click.option('-d', '--debug', is_flag=True)
@click.option('-r', '--roll', is_flag=True)
@click.pass_context
def calc_classical(ctx, bar_count, market, start_date, end_date, symbols, debug, roll):
    if debug:
        logger.setLevel(logging.DEBUG)
    m = ClassicalModelManager(bar_count=bar_count)
    m.run(start_date=start_date, end_date=end_date, symbols=symbols, market=market, roll=roll)


if __name__ == '__main__':
    cli()
