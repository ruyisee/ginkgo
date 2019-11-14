# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-11-09 13:22
"""
import logging
import click
from datetime import datetime
from ginkgo.__main__ import cli
from ginkgo.utils.logger import logger
from ginkgo import PROJECT_CONFIG_DIR, COMMANDS_LIST
from ginkgo.data_local.source_quote import QuoteModel
from ginkgo.data_local.util import datetime_to_int


@cli.command()
@click.help_option('-h', '--help', help='行情数据初始化')
@click.option('-m', '--market', default='CN', help='市场, ALL, US, HK')
@click.option('-ed', '--end_date', default=None, type=int)
@click.option('-sd', '--start_date', default=None, type=int)
@click.option('-s', '--symbols', default=None, callback=lambda _, x: x.split(',') if x else None)
@click.option('-d', '--debug', is_flag=True)
@click.pass_context
def quote_init(ctx, market, start_date, end_date, symbols, debug):
    if debug:
        logger.setLevel(logging.DEBUG)
    qm = QuoteModel(PROJECT_CONFIG_DIR, market=market)
    qm.init(symbols, start_date, end_date)


@cli.command()
@click.help_option('-h', '--help', '行情数据更新')
@click.option('-m', '--market', default='CN', help='市场, ALL, US, HK')
@click.option('-ed', '--end_date', default=None)
@click.option('-sd', '--start_date', default=None)
@click.option('-s', '--symbols', default=None, callback=lambda _, x: x.split(',') if x else None)
@click.option('-d', '--debug', is_flag=True)
@click.option('-f', '--force', is_flag=True)
@click.pass_context
def quote_update(ctx, market, end_date, start_date, symbols, force, debug):
    if debug:
        logger.setLevel(logging.DEBUG)
    if end_date is None:
        end_date = datetime_to_int(datetime.today())
    end_date = int(end_date)
    if isinstance(start_date, str):
        start_date = int(start_date)
    qm = QuoteModel(PROJECT_CONFIG_DIR, market=market)
    qm.update(symbols=symbols, start_date=start_date, end_date=end_date, f=force)


COMMANDS_LIST.append(quote_init)
