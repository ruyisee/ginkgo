# -*- coding:utf-8 -*-
"""
@author: ksf

@since: 2019-11-08 20:07
"""

from ginkgo import conf
fields_dict = conf['quote']['fields']


class Field:

    __slots__ = ['name', 'precision']

    def __init__(self, name, precision):
        self.name = name
        self.precision = precision


class Fields:

    def __init__(self, field_dict):
        self.__dict__.update(field_dict)


fields_dict = {name: Field(name, **attr) for name, attr in fields_dict.items()}
fields_manager = Fields(fields_dict)

