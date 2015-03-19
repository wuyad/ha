#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from configparser import ConfigParser

from haoss.global_def import *
from haoss.entity import *

__author__ = 'wuyadong'


def table_exists(table_name):
    sql = 'select count(table_name) from INFORMATION_SCHEMA.tables ' \
          'where TABLE_SCHEMA=\'test\' and table_name=\'{0}\''.format(table_name)
    n = db.select_int(sql)
    return n >= 1


def check_db():
    db.create_engine('root', '', 'test')
    tables = [('user', 'User'), ('apinfo', 'APInfo'), ('authap', 'AuthAP')]

    def check_or_create():
        for t in tables:
            if not table_exists(t[0]):
                log.error('table <{}> not exist, begin create it'.format(t[0]))
                n = db.update(eval(t[1] + '().__sql__()'))
                if n == 1:
                    log.info('table <{}> create.'.format(t[0]))

    check_or_create()
    # AuthAP(mac='52:54:00:16:85:54').insert()
    # AuthAP(mac='52:54:00:68:e8:6c').insert()
    # AuthAP(mac='52:54:00:12:ad:e3').insert()
    # AuthAP(mac='52:54:00:0d:3f:19').insert()
    # AuthAP(mac='52:54:00:55:db:85').insert()
    # AuthAP(mac='52:54:00:47:79:6a').insert()
    # AuthAP(mac='52:54:00:6a:a3:1c').insert()
    # AuthAP(mac='52:54:00:3d:36:02').insert()
    # AuthAP(mac='52:54:00:5c:51:2c').insert()
    # AuthAP(mac='52:54:00:59:d1:54').insert()
    return True


def check_conf():
    conf = ConfigParser()
    if conf.read(config_file):
        if conf.get('ha_server', 'port'):
            log.info('config file read successed')
            return True
    log.error('config file read failed')
    return False


def check_all():
    return check_db() and check_conf()