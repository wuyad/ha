#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

import ConfigParser

from utils.web import get, ctx, view, post
from utils import web
from portal.entity import *

config_file = 'portal.conf'


@view('hello.html')
@get('/hello')
def hello():
    uname = 'wuya'
    return dict(uname=uname)


@view('noauth.html')
@get('/noauth')
def noauth():
    return dict()


@get('/hello/')
def hello2():
    return hello()


@view('help.html')
@get('/help')
def ha_help():
    return dict()


@get('/help/')
def ha_help2():
    return ha_help()


@view('index.html')
@get('/')
def index():
    heads = dict(ctx.request.headers)

    query_string = ctx.request.query_string
    if query_string:
        heads['query_string'] = query_string

    return dict(heads=heads)


def load_request_param(param_list):
    d = {}
    for p in param_list:
        try:
            d[p] = ctx.request[p]
        except KeyError as e:
            pass
    return d


def get_gw_mac(comm_code):
    if not comm_code:
        return ''
    from pysimplesoap.client import SoapClient
    conf = ConfigParser.ConfigParser()
    conf.read(config_file)
    loc = conf.get('haoss', 'location')

    soap = SoapClient(location=loc,
                      action=loc,
                      soap_ns='soap',
                      trace=False,
                      ns=False,
                      exceptions=True)
    try:
        res = soap.GetAPInfo(comm_code=comm_code.encode('utf-8'))
    except Exception as e:
        return ''
    return str(res.ap_mac_addr)


@view('login.html')
@get('/login/')
def login():
    """/login/?gw_id=808100949391&gw_address=192.168.81.1&gw_port=80&\
    mac=aa:bb:cc:dd:cc:ee&url=http://baidu.com&comm_code=xxxxx"""

    opt_para = ['gw_id', 'gw_address', 'gw_port', 'url', 'comm_code']
    param = load_request_param(opt_para)
    # if not param.get('comm_code', ''):
    #     raise web.redirect('/noauth')
    # if not get_gw_mac(param['comm_code']):
    #     raise web.redirect('/noauth')
    gw_id = ''
    try:
        gw_id = param['gw_id']
        gw = GWInfo.get(gw_id)
        if gw:
            gw.gw_address = param['gw_address']
            gw.gw_port = param['gw_port']
            gw.update()
        else:
            gw = GWInfo(gw_id=param['gw_id'], gw_address=param['gw_address'],
                        gw_port=param['gw_port'])
            gw.insert()

    except Exception as e:
        log.error('gw info update/insert error {%s}' % e)
    try:
        gw_adv = APAdv.get(gw_id)
        if gw_adv:
            url = gw_adv.url
        else:
            url = '#'
    except Exception as e:
        log.error('ap adv read error')
    return dict(param=param, gw_id=gw_id, url=url)


def authenticate(uname, pwd):
    return True if User.find_first('where name=? and password=?', uname, pwd) else False


def make_token(uname, pwd):
    import hmac
    import hashlib
    return hmac.new('token', uname+pwd, hashlib.md5).hexdigest().upper()


@post('/redirect/')
def redirect():
    """http://GatewayIP:GatewayPort/wifidog/auth?token=[auth token]"""

    opt_para = ['uname', 'password', 'noname', 'gw_id']
    param = load_request_param(opt_para)
    uname = param['uname']
    pwd = param['password']
    token = ''
    if param.get('noname') is not None and param['noname'].lower() == 'on':
        # token = make_token('noname', 'noname')
        token = 'B9383A848D283D983699A2A5BC12EC3F'  # always OK
    elif authenticate(uname, pwd):
        token = make_token(uname, pwd)
        try:
            Token(token=token, uname=uname, password=pwd).insert()
        except Exception as e:
            pass
    else:
        token = 'xxxx'  # auth fail

    gw_id = param['gw_id']
    if not gw_id:
        raise web.redirect('/noauth')
    gw = GWInfo.get(gw_id)
    if not gw:
        raise web.redirect('/noauth')

    gw_url = 'http://{}:{}/wifidog/auth?token={}'.format(gw.gw_address, gw.gw_port, token)

    raise web.redirect(gw_url)


@get('/auth/')
def auth():
    """/auth/?stage=counters&ip=7.0.0.107&mac=00:40:05:5F:44:43&token=4f473ae3ddc5c1c2165f7a0973c57a98&
    incoming=6031353&outgoing=827770"""


    opt_para = ['stage', 'ip', 'mac', 'token', 'incoming', 'outgoing', 'token']
    param = load_request_param(opt_para)

    _auth = {
        'AUTH_DENIED': 0, # - User firewall users are deleted and the user removed.
        'AUTH_VALIDATION_FAILED': 6, # - User email validation timeout has occured and user/firewall is deleted
        'AUTH_ALLOWED': 1, # - User was valid, add firewall rules if not present
        'AUTH_VALIDATION': 5, # - Permit user access to email to get validation email under default rules
        'AUTH_ERROR': -1, # - An error occurred during the validation process
    }
    res_allowed = ['Auth: {}'.format(_auth['AUTH_ALLOWED'])]
    res_denied = ['Auth: {}'.format(_auth['AUTH_DENIED'])]

    token = ''
    try:
        token = param['token']
    except KeyError as e:
        return res_denied

    if token == 'xxxx':
        return res_denied
    elif token == 'B9383A848D283D983699A2A5BC12EC3F':
        return res_allowed
    token_info = Token.get(token)
    if not token_info:
        return res_denied
    if token_info.status == 2:
        return res_denied
    return res_allowed


@get('/auth')
def auth2():
    return auth()


@view('portal.html')
@get('/portal/')
def portal():
    """portal/?gw_id=%s"""

    opt_para = ['gw_id']
    gw_id = ''
    try:
        gw_id = ctx.request['gw_id']
    except KeyError:
        raise web.redirect('/noauth')
    gw = GWInfo.get(gw_id)
    if not gw:
        raise web.redirect('/noauth')

    gw_adv = APAdv.get(gw.gw_id)
    note = u'此AP未配置广告信息'
    url = u'无url配置'
    if gw_adv:
        note = gw_adv.remark
        url = gw_adv.url
    info = (gw_id, url, note)
    log.info('portal send')
    return dict(info=info)


@get('/portal')
def portal2():
    return portal()


@get('/ping')
def ping():
    """/ping/?gw_id=001217DA42D2&sys_uptime=742725&sys_memfree=2604&sys_load=0.03&wifidog_uptime=3861"""

    opt_para = ['gw_id', 'sys_uptime', 'sys_memfree', 'sys_load', 'wifidog_uptime']
    # param = load_request_param(opt_para)
    return 'Pong'


@get('/ping/')
def ping2():
    return ping()



