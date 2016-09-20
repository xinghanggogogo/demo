#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import json
import logging
import datetime
import random

from lib import utils
from handler.base import BaseHandler, OrderBaseHandler
from control import ctrl
from lib.decorator import check_openid, forbid_frequent_api_call
from lib.mail import Mail
from tornado.httputil import url_concat
from tornado import httpclient
from tornado.ioloop import IOLoop


PAY_KTV_ID = 85947


def query_delay(seconds=60):
    return time.time() + seconds


class NameGameHandler(BaseHandler):

    @check_openid
    async def get(self):

        openid = self.get_cookie('openid')
        config = await utils.async_common_api('/wx/share/config', dict(url=self._full_url()))
        self.render(
            'namegame/namegame.tpl',
            openid=openid,
            config=config
        )


class OrderHandler(BaseHandler):

    def gen_order_id(self, openid, charactors, sex):
        return openid + 'SO' + str(charactors) + 'D' + sex + 'T' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')[:64]

    async def prepay(self, ktv_id, openid, order_id, fee=0):

        try:
            params = {
                "op": "fastpay",
                'erpid': order_id,
                "ktvid": ktv_id,
                "paytype": "WX",
                "action": "GZH",
                "other":'namegame',
                "data": json.dumps({
                    "paraBody": '您支付了%s' % (fee / 100),
                    "paraTotalFee": fee,
                    "paraOpenId": openid,
                }),
            }

            logging.error('prepay params: %s' % params)

            url = 'http://pay.ktvsky.com/wx'
            http_client = utils.get_async_client()
            request = httpclient.HTTPRequest(url_concat(url, params), method='POST', body='',
                                             headers={'Connection': 'keep-alive'}, connect_timeout=10,
                                             request_timeout=10)

            r = await utils.fetch(http_client, request)
            r = json.loads(bytes(r.body).decode())

            logging.info(r)
            ctrl.web.update_namegame_order(data=dict(order_id=order_id, state=3, wx_pay_id=r['order']))
            return r

        except Exception as e:
            logging.error(e)
            raise utils.APIError(errcode=19003)

    @forbid_frequent_api_call(params={'cookie_keys': ['openid'], 'second': 5})
    async def post(self):

        try:
            sex = self.get_argument('sex', 'boy')
            charactors = self.get_argument('charactors', '')
            openid = self.get_cookie('openid')
            fee = int(self.get_argument('fee', 1))
        except Exception as e:
            logging.error(e)
            raise utils.APIError(errcode=10001)

        print (self.request.arguments)
        order_id = self.gen_order_id(openid, charactors, sex)
        ctrl.web.update_namegame_order(dict(order_id=order_id, openid=openid, sex=sex, charactors=charactors, fee=fee))
        prepay_data = await self.prepay(ktv_id=PAY_KTV_ID, openid=openid, order_id=order_id, fee=fee)
        logging.error(prepay_data)
        res = dict(order_id=order_id, pay_data=prepay_data)
        self.send_json(res)


class GetNamesHandler(BaseHandler):

    def get(self):
        try:
            order_id = self.get_argument('order_id')
        except Exception as e:
            logging.error(e)
            raise utils.APIError(errcode=10001)

        order = ctrl.web.get_namegame_order_by_orderid(order_id)
        gender = order['sex']
        ctrl.web.update_namegame_order(data=dict(order_id=order['order_id'], state=2))
        names_info = ctrl.web.get_names_info(gender)
        names_info = random.sample(names_info, 5)

        return self.send_json(dict(names_info=names_info))




