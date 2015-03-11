#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import time

from haoss.entity import *
from haoss.global_def import config_file


__author__ = 'wuyadong'


def start_kickoff_keeper():
    """a process to kickoff no heartbeat messages"""
    conf = configparser.ConfigParser()
    global config_file
    conf.read(config_file)
    duration = conf.getint('ha_server', 'kickoff_duration')
    cycle = conf.getint('ha_server', 'kickoff_cycle')
    while True:
        all_ap = APInfo().find_by('where status = 1')
        for ap in all_ap:
            if time.time() - ap.reg_time > duration:
                ap.status = 2
                ap.comm_code = ''
                ap.update()
                kickoff(ap.mac)
                log.info('AP {{{}}} was kickoffed'.format(ap.mac))
        time.sleep(cycle)

def kickoff(mac):
    pass
