# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-10-30 09:24
"""

import os
import shutil
import yaml
from errno import EEXIST
_here = os.path.dirname(__file__)
_config_filename = 'config.yml'


def project_config_dir():
    """
    项目根目录. 用于放置数据和配置
    """
    root = os.environ.get('GINKGO_DIR', '~/.ginkgo')
    return root


def ensure_directory(path):
    """
    检查并新建目录
    """
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == EEXIST and os.path.isdir(path):
            return
        raise


PROJECT_CONFIG_DIR = project_config_dir()


def _merge_dict(source, destination):
    """
    >>> a = { 'first' : { 'all_rows' : { 'pass' : 'dog', 'number' : '1' } } }
    >>> b = { 'first' : { 'all_rows' : { 'fail' : 'cat', 'number' : '5' } } }
    >>> _merge_dict(b, a) == { 'first' : { 'all_rows' : { 'pass' : 'dog', 'fail' : 'cat', 'number' : '5' } } }
    True
    """
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            _merge_dict(value, node)
        else:
            destination[key] = value

    return destination


def generate_config_file(directory=None):
    """
    生成配置文件
    :param directory: 配置文件保存的目录. 若为 None 则保存在默认位置
    :return: 生成的配置文件路径
    """
    if not directory:
        directory = PROJECT_CONFIG_DIR
    ensure_directory(directory)
    default_config = os.path.join(_here, '..', _config_filename)
    custom_config = os.path.abspath(os.path.join(directory, _config_filename))
    shutil.copy(default_config, custom_config)
    return custom_config


def load_config():
    """
    加载配置
    :return:
    """
    # 加载默认配置
    with open(os.path.join(_here, _config_filename), 'r', encoding='utf-8') as f:
        namespace = yaml.safe_load(f)

    # 加载用户默认配置
    try:
        with open(os.path.join(PROJECT_CONFIG_DIR, _config_filename), 'r', encoding='utf-8') as f:
            custom = yaml.safe_load(f)
            _merge_dict(custom, namespace)
    except IOError:
        pass
    return namespace