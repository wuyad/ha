#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

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

class TestOrm(unittest.TestCase):

    def setUp(self):
        db.create_engine('root', '', 'test')
        db.update('drop table if exists user')
        db.update(User().__sql__())

    def tearDown(self):
        pass

    def test_orm(self):
        u = User(id=10190, name='Michael', email='orm@db.org')
        r = u.insert()
        self.assertEqual(u.email, 'orm@db.org')
        self.assertEqual(u.passwd, '******')
        self.assertEqual(u.last_modified > (time.time() - 2), True)
        f = User.get(10190)
        self.assertEqual(f.name, 'Michael')
        self.assertEqual(f.email, 'orm@db.org')
        f.email = 'changed@db.org'
        r = f.update()  #change email but email is non-updatable!
        self.assertEqual(len(User.find_all()), 1)
        g = User.get(10190)
        self.assertEqual(g.email, u'orm@db.org')
        r = g.delete()
        self.assertEqual(len(db.select('select * from user where id=10190')),
                         0)

        log.info(User().__sql__())
        '''-- generating SQL for user:
        create table user (
        id bigint not null,
        name varchar(255) not null,
        email varchar(255) not null,
        passwd varchar(255) not null,
        last_modified real not null,
        id)
        );
        '''

