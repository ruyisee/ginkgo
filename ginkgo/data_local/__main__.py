# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-11-09 13:22
"""
import logging
import click
from ginkgo.__main__ import cli
from ginkgo.utils.logger import logger
from ginkgo import PROJECT_CONFIG_DIR, COMMANDS_LIST
from ginkgo.data_local.source_quote import QuoteModel


@cli.command()
@click.help_option('-h', '--help')
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
@click.help_option('-h', '--help')
@click.option('-m', '--market', default='CN', help='市场, ALL, US, HK')
@click.option('-ed', '--end_date', default=None)
@click.option('-sd', '--start_date', default=None)
@click.option('-s', '--symbols', default=None, callback=lambda _, x: x.split(',') if x else None)
@click.option('-d', '--debug', is_flag=True)
@click.pass_context
def quote_update(ctx, market, start_date, end_date, symbols, debug):
    if debug:
        logger.setLevel(logging.DEBUG)
    qm = QuoteModel(PROJECT_CONFIG_DIR, market=market)
    qm.init(symbols, start_date, end_date)

COMMANDS_LIST.append(quote_init)
