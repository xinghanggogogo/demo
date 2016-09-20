#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import json
import logging
import datetime
import random

from lib import utils
from handler.base import BaseHandler
from control import ctrl
from lib.decorator import check_openid, forbid_frequent_api_call
from lib.mail import Mail
from tornado.httputil import url_concat
from tornado import httpclient
from tornado.ioloop import IOLoop


class NameGameHandler(BaseHandler):

    @check_openid
    async def get(self):

        openid = self.get_cookie('openid')
        user_info = ctrl.web.get_namegame_order(openid)  # user和order一张表
        config = await utils.async_common_api('wx/share/cofig', dict(url=self._full_url()))
        self.render(
            'namegame/namegame.py',
            openid=openid,
            user_info=user_info,
            config=config
        )


class OrderHandler(BaseHandler):

    def gen_order_id(self, openid, charactors, sex):
        return openid + 'SO' + str(charactors) + 'D' + sex+ 'T' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')[:64]

    def query_delay(seconds=60):
        return time.time() + seconds

    async def prepay(self, openid, order_id, fee=0):

        try:
            params = {
                "op": "fastpay",
                'erpid': order_id,
                "paytype": "WX",
                "action": "GZH",
                "data": json.dumps({
                    "paraBody": '你支付了%.02f元' % (fee / 100),
                    "paraTotalFee": fee,
                    "paraOpenId": openid,
                }),
            }

            logging.error('prepay params: %s' % params)

            url = 'http://pay.ktvsky.com/wx'
            http_client = utils.get_async_client()
            request = httpclient.HTTPRequest(url_concat(url, params), method='POST', body='',
                                             headers={'Connection': 'keep-alive'}, connect_timeout=10, request_timeout=10)

            r = await utils.fetch(http_client, request)
            r = json.loads(bytes(r.body).decode())

            logging.info(r)
            ctrl.web.update_namegame_order(order_id, data=dict(state=3, wx_pay_id=r['order']))
            IOLoop.current().add_timeout(self.query_delay(), self.pay_query, order_id, loop=5)
            return r

        except Exception as e:
            logging.error(e)
            raise utils.APIError(errcode=19003)

    async def pay_query(self, order_id, loop=1):

        logging.info("\n\nloop=%s" % loop)
        order = ctrl.web.get_namegame_order(order_id)
        if not order:
            raise utils.APIError(errcode=10001)
        try:
            params = {
                "op": "query",
                "paytype": 'WX',
                "data": json.dumps({
                    "paraOutTradeNo": order['wx_pay_id'],
                }),
            }
            url = 'http://pay.ktvsky.com/wx'
            http_client = utils.get_async_client()
            request = httpclient.HTTPRequest(url_concat(url, params), method='POST', body='',
                                             headers={'Connection': 'keep-alive'}, connect_timeout=10, request_timeout=10)

            res = await utils.fetch(http_client, request)
            res = json.loads(bytes(res.body).decode())
            logging.info(res)

            if utils.is_success_pay('wx', res):
                IOLoop.current().spawn_callback(self.after_pay, order)
                return res

        except Exception as e:
            logging.error(e)
            if loop > 0:
                IOLoop.current().add_timeout(self.query_delay(), self.pay_query, order_id, loop=loop - 1)
            raise utils.APIError(errcode=19004)

        if loop > 0:
            IOLoop.current().add_timeout(self.query_delay(), self.pay_query, order_id, loop=loop - 1)

        return res

    async def after_pay(self, order):

        logging.error('in IOLoop spawn_callback:%s' % order)
        username = order['username']
        email = order['email']
        ctrl.web.update_namegame_order(order['order_id'], data=dict(state=2))

        names_random_ids = random.sample(range(0, 1868), 5)
        names_info = []
        names_info.append(ctrl.get_name_info_byids(names_random_ids))

        mail = Mail()
        subject = 'mtv审核提醒/建议'
        content = self.render_string('mail/namegame.mail', username=username, names_info=names_info)
        logging.info("to: %s, content: %s" % (email, content))
        mail.send(subject, content, [email])

    @forbid_frequent_api_call(params={'cookie_keys': ['openid'], 'second': 5})
    async def post(self):

        try:
            sex = self.get_argument('sex', 'male')
            charactors = self.get_argument('chacractors', '')
            username = self.get_argument('username')
            email = self.get_argument('email')
            openid = self.get_cookie('openid')
            fee = int(self.get_argument('fee', 9.9))
        except Exception as e:
            logging.error(e)
            raise utils.APIError(errcode=10001)
        order_id = self.gen_order_id(openid, charactors, sex)
        ctrl.update_namegame_order(order_id, dict(openid=openid, username=username, email=email, sex=sex, chacractors=charactors, fee=fee))
        
        prepay_data = await self.prepay(openid=openid, order_id=order_id, fee=fee)
        logging.error(prepay_data)

        res = dict(order_id=order_id, pay_data=prepay_data)
        self.send_json(res)

    async def get(self):

        try:
            order_id = self.get_argument('order_id')
        except Exception as e:
            logging.error(e)
            raise utils.APIError(errcode=10001)

        res = await self.pay_query(order_id)
        is_pay = 1 if utils.is_success_pay('wx', res) else 0
        nickname = ''
        if is_pay:
            namegame_order = ctrl.web.get_namegame_order(order_id)
            nickname = namegame_order['nickname']

        return self.send_json(dict(is_pay=is_pay, nickname=nickname))


#支付调用的另一个版本:
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

class NameGameHandler(BaseHandler):

    @check_openid
    async def get(self):

        openid = self.get_cookie('openid')
        user_info = ctrl.web.get_namegame_order(openid)  # user和order一张表
        config = await utils.async_common_api('wx/share/cofig', dict(url=self._full_url()))
        self.render(
            'namegame/namegame.py',
            openid=openid,
            user_info=user_info,
            config=config
        )


class OrderHandler(OrderBaseHandler):

    def gen_order_id(self, openid, charactors, sex):
        return openid + 'SO' + str(charactors) + 'D' + sex+ 'T' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')[:64]

    async def get(self):
        try:
            order_id = self.get_argument('order_id')
        except Exception as e:
            logging.error(e)
            raise utils.APIError(errcode=10001)

        res = await self.pay_query(PAY_KTV_ID, order_id)
        is_pay = 1 if utils.is_success_pay('wx', res) else 0
        nickname = ''
        if is_pay:
            namegame_order = ctrl.web.get_namegame_order(order_id)
            nickname = namegame_order['nickname']

        return self.send_json(dict(is_pay=is_pay, nickname=nickname))

    @forbid_frequent_api_call(params={'cookie_keys': ['openid'], 'second': 5})
    async def post(self):
        try:
            openid = self.get_cookie('openid')
            username = self.get_argument('username')
            email = self.get_argument('email')
            sex = self.get_argument('sex', 'boy')
            charactors = self.get_argument('charactors', '')
            fee = int(self.get_argument('fee', 68))
            body = self.get_argument('body', '')
        except Exception as e:
            logging.error(e)
            raise utils.APIError(errcode=10001)

        order_id = self.gen_order_id(openid, charactors, sex)
        ctrl.web.update_namegame_order(data=dict(order_id=order_id, openid=openid, username=username, email=email, sex=sex, charactors=charactors, fee=fee))
        
        prepay_data = await self.prepay(PAY_KTV_ID, openid, order_id, fee, body, other='namegame')

        logging.error(prepay_data)
        res = dict(order_id=order_id, pay_data=prepay_data)
        self.send_json(res)

    def after_prepay(self, order_id, prepay):
        ctrl.web.update_namegame_order(order_id, data=dict(state=3, wx_pay_id=prepay['order']))

    async def after_pay(self, order):
        logging.error('in IOLoop spawn_callback:%s' % order)
        username = order['username']
        gender = order['sex']
        email = order['email']
        ctrl.web.update_namegame_order(order['order_id'], data=dict(state=2))
        names_info = ctrl.web.get_names_info(gender)
        names_info = random.sample(names_info, 5)

        mail = Mail()
        subject = '最适合您孩子的英文名'
        content = self.render_string('mail/namegame.mail', username=username, names_info=names_info)
        logging.info("to: %s, content: %s" % (email, content))
        mail.send(subject, content, [email])