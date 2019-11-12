# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-11-10 18:33
"""
import os
import codecs
from distutils.core import setup


def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='ginkgo',
    version=read('ginkgo/VERSION.txt'),
    packages=['ginkgo', 'ginkgo.analysis', 'ginkgo.core', 'ginkgo.data_local',
              'ginkgo.utils'],
    author='ksf',
    author_email='timeless.go@foxmail.com',
    description='stock local data',
    package_data={'': ['*.*']},
    include_package_data=True,
    url='https://github.com/fsksf/ginkgo',
    entry_points={
        "console_scripts": [
            "ginkgo = ginkgo.__main__:entry_point"
        ]
    },
    install_requires=read('requirements.txt')
)