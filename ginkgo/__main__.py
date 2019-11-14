# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-10-29 08:30
"""

import click
from ginkgo.config import generate_config_file
from ginkgo import COMMANDS_LIST



@click.group()
@click.help_option('-h', '--help', help='请选择要执行的command')
@click.pass_context
def cli(ctx):
    pass


@cli.command()
@click.help_option('-h', '--help', help='获取用户配置文件保存到~/.ginkgo/config.yml, 或者用户自定义位置')
@click.pass_context
def gen_config(ctx):
    generate_config_file()


COMMANDS_LIST.append(gen_config)
from ginkgo.data_local.__main__ import *
from ginkgo.analysis.__main__ import *


def load_command():
    for command in COMMANDS_LIST:
        cli.add_command(command)


def entry_point():
    load_command()
    cli()


if __name__ == '__main__':
    entry_point()
