#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__author__ = 'wuyadong'


config_file = 'haoss.conf'
pkg_def = {
    'REGI': ('!17s', 'do_register'),
    'RPRE': ('!4s40s', 'do_register_response'),
    'LOGO': ('!17s', 'do_logout'),
    'RPLO': ('!4s', 'do_logout_response'),
    'KEEP': ('!17s', 'do_keep_alive'),
}


