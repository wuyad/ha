#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import struct
import socket
import time
from multiprocessing.pool import Pool

from haoss.global_def import config_file
from haoss.global_def import pkg_def


__author__ = 'wuyadong'


def main():
    conf = configparser.ConfigParser()
    # global config_file
    conf.read(config_file)
    port = conf.getint('ha_server', 'port')
    server_ip = conf.get('ha', 'server_ip')
    pool_n = conf.getint('ha', 'pool')

    pool = Pool()
    for i in range(pool_n):
        pool.apply_async(sub_main, args=(server_ip, port, i))
    pool.close()
    pool.join()


def sub_main(server_ip, port, sub_n):
    print('sub process {} started'.format(sub_n))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((server_ip, port))
    except ConnectionRefusedError:
        print('Connection Refused Error, Server may DOWN')
        s.close()
        return
    ap = ApClient()
    ap.sock = s
    ap.register()
    for i in range(5):
        ap.keepalive()
        time.sleep(3)
    ap.logout()
    s.close()
    print('sub process {} closed'.format(sub_n))


class ApClient:
    def __init__(self):
        macs = [b'52:54:00:0d:3f:19',
                b'52:54:00:12:ad:e3',
                b'52:54:00:16:85:54',
                b'52:54:00:3d:36:02',
                b'52:54:00:47:79:6a',
                b'52:54:00:55:db:85',
                b'52:54:00:59:d1:54',
                b'52:54:00:5c:51:2c',
                b'52:54:00:68:e8:6c',
                b'52:54:00:6a:a3:1c',
                b'52:54:01:0d:3f:19',
                b'52:54:01:12:ad:e3',
                b'52:54:01:16:85:54',
                b'52:54:01:3d:36:02',
                b'52:54:01:47:79:6a',
                b'52:54:01:55:db:85',
                b'52:54:01:59:d1:54',
                b'52:54:01:5c:51:2c',
                b'52:54:01:68:e8:6c',
                b'52:54:01:6a:a3:1c']
        from random import randint
        self.mac = macs[randint(0,len(macs))]
        # self.mac = b'52:54:01:0d:3f:19'  # for test, no auth
        self.comm_code = ''

    def register(self):
        print('Begin send REGI')
        fmt = pkg_def['REGI'][0]
        buf = struct.pack(fmt, self.mac)
        n = self.sock.send(b'REGI')
        assert n == 4, 'send fail REGI'
        n = self.sock.send(buf)
        assert n == 17, 'send fail REGI'
        print('End send REGI')

        print('Begin recv RPRE')
        buf = self.sock.recv(4)
        assert buf == b'RPRE', buf
        fmt = pkg_def['RPRE'][0]
        n = struct.calcsize(fmt)
        buf = self.sock.recv(n)
        assert n == len(buf)
        status, comm_code = struct.unpack(fmt, buf)
        self.comm_code = comm_code
        print('End recv RPRE [status:{}, comm_code:{}]'.format(status.decode(),
                                                               comm_code.decode()))

    def keepalive(self):
        fmt = pkg_def['KEEP'][0]
        buf = struct.pack(fmt, self.mac)
        try:
            n = self.sock.send(b'KEEP')
            n = self.sock.send(buf)
        except Exception as e:
            print('Error send KEEP {{{}}}'.format(e))
        else:
            print('End sent KEEP')

    def logout(self):
        print('Begin send LOGO')
        fmt = pkg_def['LOGO'][0]
        buf = struct.pack(fmt, self.mac)
        n = self.sock.send(b'LOGO')
        assert n == 4, 'send fail LOGO'
        n = self.sock.send(buf)
        assert n == 17, 'send fail LOGO'
        print('End send LOGO')

        print('Begin recv LOGO')
        buf = self.sock.recv(4)
        assert buf == b'RPLO', buf
        fmt = pkg_def['RPLO'][0]
        n = struct.calcsize(fmt)
        buf = self.sock.recv(n)
        assert n == len(buf)
        status = struct.unpack(fmt, buf)
        print('End recv LOGO [status:{}]'.format(status[0].decode()))


if __name__ == '__main__':
    main()
