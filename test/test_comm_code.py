#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from haoss import comm_code
from utils.log import log


__author__ = 'wuyadong'


class Test_Comm_Code(unittest.TestCase):
    def test_comm_code(self):
        # for i in range(10):
        #     mac = comm_code.randomMAC()
        #     print(mac)
        mac = '52:54:00:60:46:fd'
        code = comm_code.CommCode(mac)
        self.assertEqual(str(code), 'D0AB12A3B65C0EE735364007D56E5C235A2016B5')