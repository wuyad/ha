#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from utils.db import *


__author__ = 'wuyadong'


class TestDB(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.WARNING)
        create_engine('root', '', 'test')
        update('drop table if exists user')
        update(
            'create table user (id int primary key, name text, '
            'email text, passwd text, last_modified real)')

    def tearDown(self):
        pass

    def test_update(self):
        u1 = dict(id=1000, name='Michael', email='michael@test.org',
                  passwd='123456', last_modified=time.time())
        n = insert('user', **u1)
        self.assertEqual(n, 1)
        u2 = select_one('select * from user where id=?', 1000)
        self.assertEqual(u2.email, 'michael@test.org')
        self.assertEqual(u2.passwd, '123456')
        n = update('update user set email=?, passwd=? where id=?',
                   'michael@example.org', '654321', 1000)
        self.assertEqual(n, 1)
        u3 = select_one('select * from user where id=?', 1000)
        self.assertEqual(u3.email, 'michael@example.org')
        self.assertEqual(u3.passwd, '654321')
        n = update('update user set passwd=? where id=?', '***',
                   '123\' or id=\'456')
        self.assertEqual(n, 0)

    def test_dict(self):
        d1 = Dict()
        d1['x'] = 100
        self.assertEqual(d1.x, 100)
        d1['y'] = 200
        self.assertEqual(d1.y, 200)
        d2 = Dict(a=1, b=2, c='3')
        self.assertEqual(d2.c, '3')
        with self.assertRaises(AttributeError):
            d2.empty
        with self.assertRaises(KeyError):
            d2['empty']
        d3 = Dict(('a', 'b', 'c'), (1, 2, 3))
        self.assertEqual(d3.a, 1)
        self.assertEqual(d3.b, 2)
        self.assertEqual(d3.c, 3)

    def test_insert(self):
        u1 = dict(id=2000, name='Bob', email='bob@test.org', passwd='bobobob',
                  last_modified=time.time())
        n = insert('user', **u1)
        self.assertEqual(n, 1)
        u2 = select_one('select * from user where id=?', 2000)
        self.assertEqual(u2.name, 'Bob')
        from mysql.connector.errors import IntegrityError

        with self.assertRaises(IntegrityError):
            insert('user', **u2)

    def test_transaction(self):
        def update_profile(id, name, rollback):
            u = dict(id=id, name=name, email='%s@test.org' % name, passwd=name,
                     last_modified=time.time())
            insert('user', **u)
            r = update('update user set passwd=? where id=?', name.upper(), id)
            if rollback:
                raise Exception('will cause rollback')

        with transaction():
            update_profile(900301, 'Python', False)
        ret = select_one('select * from user where id=?', 900301).name
        self.assertEqual(ret, 'Python')
        with self.assertRaises(Exception):
            with transaction():
                update_profile(900302, 'Ruby', True)
        ret = select('select * from user where id=?', 900302)
        self.assertEqual(ret, [])

    def test_select(self):
        u1 = dict(id=200, name='Wall.E', email='wall.e@test.org',
                  passwd='back-to-earth', last_modified=time.time())
        u2 = dict(id=201, name='Eva', email='eva@test.org',
                  passwd='back-to-earth', last_modified=time.time())
        self.assertEqual(insert('user', **u1), 1)
        self.assertEqual(insert('user', **u2), 1)
        l = select('select * from user where id=?', 900900900)
        self.assertEqual(l, [])
        l = select('select * from user where id=?', 200)
        self.assertEqual(l[0].email, 'wall.e@test.org')
        l = select('select * from user where passwd=? order by id desc',
                   'back-to-earth')
        self.assertEqual(l[0].name, 'Eva')
        self.assertEqual(l[1].name, 'Wall.E')

    def test_connection(self):
        with connection():
            u = dict(id=202, name='wuyad', email='wall.e@test.org',
                      passwd='back-to-earth', last_modified=time.time())
            insert('user', **u)
            ret = select('select name from user where id=?', 202)
            self.assertEqual(ret[0].name, 'wuyad')
            ret = update('update user set name=? where id=?', ret[0].name.upper(), 202)
            self.assertEqual(ret, 1)
            ret = select('select name from user where id=?', 202)
            self.assertEqual(ret[0].name, 'WUYAD')


# if __name__ == '__main__':
# unittest.main()
# suite = unittest.TestSuite()
# suite.addTest(TestDB())
