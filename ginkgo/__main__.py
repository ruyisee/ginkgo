# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-10-29 08:30
"""

import click


@click.group()
@click.help_option('-h', '--help')
@click.pass_context
def cli(ctx):
    pass


def load_command():
    for command in COMMANDS_LIST:
        cli.add_command(command)


if __name__ == '__main__':
    from ginkgo.data_local.__main__ import *
    from ginkgo.analysis.__main__ import *
    load_command()
    cli()