#!/usr/bin/env python
# encoding: utf-8

"""Paras staattisien sivujen Pythonistinen generaattori

Usage: pasta [-hv] [--verbose] [-d <path>|--directory <path>]

  -h, --help                     Print this help
  -v, --verbose                  Be verbose
  -d <path>, --directory <path>  Use <path> as base path to source files
"""

from docopt import docopt
from pastaspyge import Pasta
import logging

if __name__ == '__main__':
    arguments = docopt(__doc__, version='0.001a')
    root = None
    logging.basicConfig()
    logger = logging.getLogger()
    if arguments['--verbose']:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.ERROR)
    if arguments['--directory']:
        root = arguments['--directory']
    elif arguments['-d']:
        root = arguments['-d']
    a = Pasta(root=root)
    a.generate_all()