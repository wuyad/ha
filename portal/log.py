#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'wuyadong'

import logging
import logging.config


logging.config.fileConfig("portal_log.conf")
log = logging.getLogger()

if __name__ == '__main__':
    log.debug('This is debug message')
    log.info('This is info message')
    log.warning('This is warning message')

