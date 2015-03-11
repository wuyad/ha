#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socketserver
import configparser
import struct

from haoss.comm_code import *
from haoss.entity import *
from haoss.global_def import config_file
from haoss.global_def import pkg_def


__author__ = 'wuyadong'


def start_ha_server():
    conf = configparser.ConfigParser()
    global config_file
    conf.read(config_file)
    port = conf.getint('ha_server', 'port')
    log.info('HAOSS server started with port {}.'.format(port))
    try:
        server = socketserver.ForkingTCPServer(('', port), ha_hangler)
    except Exception as e:
        print(e)
        return
    server.serve_forever()


class ha_hangler(socketserver.StreamRequestHandler):
    """request processor when recv msg from HA"""

    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)
        self.package_body = ''
        self.comm_code = ''
        self.mac_addr = ''

    def setup(self):
        # self.timeout == 10
        super().setup()

    def handle(self):
        action = ''
        while True:
            try:
                action = self.request.recv(4)
            except Exception as e:
                print(e)
                break
            if action == b'':
                log.info('Closed by peer')
                return
            global pkg_def
            act = action.decode()
            try:
                fmt, caller = pkg_def[act]
            except KeyError as e:
                log.error('Wrong package id {}'.format(act))
                return
            n = struct.calcsize(fmt)
            buf = self.request.recv(n)
            try:
                t = struct.unpack(fmt, buf)
            except Exception as e:
                print('Package format error {{{}}}'.format(e))
            self.package_body = t
            eval('self.' + caller + '()')

    def do_register(self):
        mac_addr = self.package_body[0].decode()
        auth_ap = AuthAP.get(mac_addr)
        res = 'OK'
        ap = APInfo(mac=mac_addr)
        if auth_ap is None:
            ap.comm_code = ''
            res = 'FAIL'
        else:
            ap = APInfo.get(mac_addr)
            try:
                if ap is None:
                    ap = APInfo(mac=mac_addr, status=1)
                    ap.comm_code = str(CommCode(mac_addr))
                    ap.insert()
                else:
                    ap.comm_code = str(CommCode(mac_addr))
                    ap.reg_time = time.time()
                    ap.status = 1
                    ap.update()
            except:
                res = 'FAIL'
        self.comm_code = ap.comm_code
        self.mac_addr = ap.mac
        self.do_register_response(res)

    def do_register_response(self, res):
        global pkg_def
        fmt, _ = pkg_def['RPRE']
        n = self.request.send(b'RPRE', 4)
        assert n == 4, 'RPRE header send failed.'
        buf = struct.pack(fmt, res.encode(), self.comm_code.encode())
        try:
            self.request.send(buf)
        except:
            log.info('RPRE send FAIL {{{}}}'.format(self.mac_addr))
        else:
            log.info('RPRE send OK {{{}}}'.format(self.mac_addr))

    def do_logout(self):
        mac_addr = self.package_body[0].decode()
        res = 'OK'
        ap = APInfo.get(mac_addr)
        if ap is None:
            res = 'FAIL'
        else:
            ap.comm_code = ''
            ap.status = 0
            ap.update()
            self.comm_code = ap.comm_code
            self.mac_addr = ap.mac
        self.do_logout_response(res)

    def do_logout_response(self, status):
        global pkg_def
        fmt, _ = pkg_def['RPLO']
        n = self.request.send(b'RPLO', 4)
        assert n == 4, 'RPLO header send failed.'
        buf = struct.pack(fmt, status.encode())
        try:
            self.request.send(buf)
        except:
            log.info('RPLO send FAIL {{{}}}'.format(self.mac_addr))
        else:
            log.info('RPLO send OK {{{}}}'.format(self.mac_addr))

    def do_keep_alive(self):
        ap = APInfo().get(self.package_body[0])
        if ap is None:
            log.info('Hear Beats wrong, Need register first')
        else:
            if ap.status != 1:
                log.info('Hear Beats timeout, Need register')
            else:
                ap.reg_time = time.time()
                ap.update()
                log.info('Heart Beats OK {{{}}}'.format(self.mac_addr))


