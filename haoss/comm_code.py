#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import hmac

__author__ = 'wuyadong'


def random_mac():
    mac = [0x52, 0x54, 0x00,
           random.randint(0x00, 0x7f),
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff)]
    return ':'.join(map(lambda x: "%02x" % x, mac))


class CommCode:
    """genorator communication code by AP's MAC"""

    def __init__(self, mac):
        self.mac = mac

    def _gen_code(self):
        return hmac.new('生命是那条无休无止的河'.encode(), self.mac.upper().encode(), 'sha1').hexdigest().upper()

    def __str__(self):
        return self._gen_code()
