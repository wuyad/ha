#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__author__ = 'wuyadong'

import os
from multiprocessing import Process

from utils.orm import *
from haoss.check import check_all
from haoss.ha_server import start_ha_server
from haoss.kickoff_keeper import start_kickoff_keeper


if __name__ == '__main__':
    log.info('Starting HAOSS server...')
    if not check_all():
        log.error('HAOSS server failed to start.')
        os._exit(-1)
    k = Process(target=start_kickoff_keeper)
    k.start()
    start_ha_server()



