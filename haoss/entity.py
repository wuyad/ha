#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from utils.orm import *

__author__ = 'wuyadong'


class User(Model):
    id = IntegerField(primary_key=True)
    name = StringField()
    email = StringField(updatable=False)
    passwd = StringField(default=lambda: '******')
    last_modified = FloatField()

    def pre_insert(self):
        self.last_modified = time.time()


class APInfo(Model):
    mac = StringField(ddl='varchar(19)', primary_key=True)
    comm_code = StringField(ddl='varchar(42)', updatable=True)
    reg_time = FloatField()
    status = TinyIntegerField(default=0)  # 0-offline 1-online 2-kickoff
    err_n = TinyIntegerField(default=0)  # TODO: now not use

    def pre_insert(self):
        self.reg_time = time.time()


class AuthAP(Model):
    mac = StringField(ddl='varchar(19)', primary_key=True)


if __name__ == '__main__':
    AuthAP(mac='afdasf')
