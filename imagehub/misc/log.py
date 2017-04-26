# coding: utf-8

'''
Log package for Python. Based on module 'logging' and 'pprint' in
comp.lang.python.

Copyright (C) 2001-2014 hanson leung. All Rights Reserved.

To use, simply 'import log' and log away!
'''

import logging as log
import pprint


def warn(msg):
    log.warn(str(msg))


def info(msg):
    log.info(str(msg))


def debug(msg):
    log.debug(str(msg))


def save_page(s, filename='RESOURCE', mode='w'):
    with(open(filename, mode)) as f:
        f.write(s)


class PrettyPrinter(pprint.PrettyPrinter):
    def format(self, object, context, maxlevels, level):
        if isinstance(object, unicode):
            return (object.encode('utf8'), True, False)
        return pprint.PrettyPrinter.format(self, object, context, maxlevels, level)
pu = PrettyPrinter()

pp = pprint.PrettyPrinter()
