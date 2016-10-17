#调用pay_cut使用支付功能
class OrderHandler(BaseHandler):

	async def prepay(self, openid, erp_id, ktv_id, fee):
		try:
			other={
				#附加信息
			}
			params = {
				"tp": "", #有值就需要特殊分成
				"op": "fastpay",
				"ktvid": ktv_id, #相关就传，不相关就不传
				'erpid': erp_id,
				"paytype": "WX",
				"action": "GZH",
				"other": json.dumps(other),
				"data": json.dumps({
					"paraBody": '打赏美女了%.02f元' % (pay_fee / 100),
					"paraTotalFee": fee,
					"paraOpenId": openid,
				}),
			}
			logging.error('prepay params: %s' % params)

			url = 'http://pay.ktvsky.com/wx'
			http_client = utils.get_async_client()
			request = httpclient.HTTPRequest(url_concat(url, params), method='POST', body='',
				headers={'Connection': 'keep-alive'}, connect_timeout=10, request_timeout=10)

			r = await utils.fetch(http_client, request) #通过pay_cut接口得知，这个r包含了调用微信统一下单接口的返回的字典内容，还包含了order_id,等4个字段。
			r = json.loads(bytes(r.body).decode())

			logging.info(r)
			ctrl.web.update_by_order(data=dict(erp_id, state=3, order_id=r['order_id'])) #这里的order_id区别与erp_id，是传给微信的，长度应该符合规范
			IOLoop.current().add_timeout(query_delay(), self.pay_query, r['order_id'], loop=5)
			return r

		except Exception as e:
			logging.error(e)
			raise utils.APIError(errcode=19003)

	async def pay_query(self, order_id, loop=1):
		logging.info("\n\npay_query_loop=%s, order_id=%s"%(loop, order_id))
		order = ctrl.web.get_order_by_order_id(order_id)
		if not order:
			raise utils.APIError(errcode=10001)
		try:
			params = {
				"op": "query",
				"ktvid": order['ktv_id'],
				"paytype": 'WX',
				"data": json.dumps({
					"paraOutTradeNo": order['order_id'],
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
				order['wx_pay_id'] = res['transaction_id']#这个是微信的线上订单号，由order_id长须订单状态，如果确认支付成功返回微信的线上订单id
				await self.after_pay(order)

		except Exception as e:
			logging.error(e)
			if loop > 0:
				IOLoop.current().add_timeout(query_delay(), self.pay_query, order_id, loop=loop-1)
			raise utils.APIError(errcode=19004)
		if loop > 0:
			IOLoop.current().add_timeout(query_delay(), self.pay_query, order_id, loop=loop-1)
		return res

	async def after_pay(self, order):
		logging.error('after_pay_callback: %s' % order)
		order_id = order['order_id']
		ctrl.web.update_by_order(data=dict(order_id= order_id, state=2))
		self.send_json(dict(is_pay=1))

	@forbid_frequent_api_call(params={'cookie_keys': ['openid'], 'seconds': 5})
	async def post(self):
		try:
			arg1 = int(self.get_argument(''))
			arg2 = self.get_argument('', '')
			openid = self.get_cookie('openid')
			fee= int(self.get_argument('fee', 200))
		except Exception as e:
			logging.error(e)
			raise utils.APIError(errcode=10001)

		key = 'order_%s' % openid
		if not ctrl.rs.setnx(key, 1):
			raise utils.APIError(errcode=18001, errmsg='已经支付过')
		ctrl.rs.expire(key, 3*60)
		erp_id = gen_erp_id(openid, arg1, arg2)
		ctrl.web.update_order_with_erp_id(dict(openid=openid, erp_id=erp_id, fee=fee))
		prepay_data = await self.prepay(openid, erp_id, ktv_id,fee)
		logging.error(prepay_data)
		res = dict(order_id=prepay_data['order_id'], pay=prepay_data)
		self.send_json(res)

	async def get(self):
		'''用户输入密码支付后，微信返回预支付成功200，由前端主动来调查询订单是否成功'''
		try:
			order_id = self.get_argument('order_id')
		except Exception as e:
			logging.error(e)
			raise utils.APIError(errcode=10001)
		res = await self.pay_query(order_id)
        		is_pay = res['is_pay']
        		return self.send_json(dict(is_pay=is_pay))

class AferPayHandler(BaseHandler):
	#如果查询订单is_pay=1,支付成功
    	def get(self):
	        	try:
	            		order_id = self.get_argument('order_id')
	        	except Exception as e:
	            		logging.error(e)
	            		raise utils.APIError(errcode=10001)

		order = ctrl.web.get_namegame_order_by_order_id(order_id)
		gender = order['sex']
		names_info = ctrl.web.get_names_info(gender)
		names_info = random.sample(names_info, 5)
		return self.send_json(dict(names_info=names_info))

#微信调用，主动返回支付成功的out_trade_id
class OrderCbHandler(BaseHandler):

    @gen.coroutine
    def post(self):
        logging.info(self.request.body)
        res = wxpay.WeiXinResponse(self.request.body).verify()
        if not res:
            raise utils.APIError(errcode=10001, errmsg='验签错误')
        order_id = res['out_trade_no']
        ctrl.web.update_namegame_order(data=dict(order_id=order_id, state=2))


#一个另起炉灶的支付工程：
#!/usr/bin/env python
# -*- coding: utf-8 -*-

PAY_KTV_ID = 85947
WX_USERINFO_GRANT_URL = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid={appid}&redirect_uri={redirect_uri}&response_type=code&scope=snsapi_base&state={state}&connect_redirect=1#wechat_redirect'#静默获取openid,无需跳转，无法获得用户信息
FETCH_OPENID_URL = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid={appid}&secret={secret}&code={code}&grant_type=authorization_code'
WX_REDIRECT_URL = 'https://erp.ktvsky.com/ng/wx' #公众号登记授权

# 收银员等级app
WX_SYY_CONF = {
	'appid': 'wx790c59cfd383eb60',
	'appsecret': '0086acb983365eb952fc37cd52ef4e83'
}

MAX_LOOP = 1
QUERY_DELAY = 60
COUPON_SEND_DELAY = 20

def delay_times(loop=MAX_LOOP):
	res = time.time() + QUERY_DELAY * (MAX_LOOP - loop + 2)
	logging.debug(datetime.datetime.fromtimestamp(res).strftime('%Y-%m-%d %H:%M:%S'))
	return res

def query_delay(seconds=60):
	return time.time() + seconds

def wx_auth(func):
	def wrap(*args, **kw):
		self = args[0]
		state = self.request.uri
		openid = self.get_cookie('openid')
		if openid:
			return func(*args, **kw)
		if self.request.path in ('/ng/ktv/order/namegame'):
			state = '/ng/ktv/order/namegame'
		if '?' in state:
			path, params = state.split('?', 1)
			param_list = params.split('&')
			param_list = list(filter(lambda x: 'from' not in x and 'isappinstalled' not in x, param_list))
			state = path + '?' + '&'.join(param_list)
		url = WX_USERINFO_GRANT_URL.format(appid=WX_SYY_CONF['appid'], redirect_uri=quote(WX_REDIRECT_URL), state=quote(state))
		return self.redirect(url)
	return wrap


class WxCallBackHandler(BaseHandler):

	async def _get_openid(self, code):
		key = 'code_%s' % code
		v = ctrl.rs.get(key)
		if v:
			return v.decode()
		url = FETCH_OPENID_URL.format(appid=WX_SYY_CONF['appid'], secret=WX_SYY_CONF['appsecret'], code=code)
		http_client = utils.get_async_client()
		request = utils.http_request(url)
		response = await http_client.fetch(request)
		response = json.loads(response.body.decode())
		logging.info(response)
		ctrl.rs.set(key, response['openid'], 10*60)
		return response['openid']

	async def get(self):
		state = self.get_argument('state', '/ng/ktv/order/namegame')
		code = self.get_argument('code', '')
		if code:  # 有code, 是已经授权跳转回来的, 则获取openid
			openid = await self._get_openid(code)
			self.set_cookie('openid', openid)
			return self.redirect(unquote(state))

		url = WX_USERINFO_GRANT_URL.format(
			appid=WX_SYY_CONF['appid'],
			redirect_uri=quote(WX_REDIRECT_URL),
			state=state
		)
		# 跳转去授权
		return self.redirect(url)


class NameGameHandler(BaseHandler):

	@wx_auth
	async def get(self):

		openid = self.get_cookie('openid')
		config = await utils.async_common_api('/wx/share/config', dict(url=self._full_url(), flag=1)) #收银员登记config
		self.render(
			'namegame/namegame.tpl',
			openid=openid,
			config=config)


class OrderHandler(BaseHandler):

	def gen_order_id(self, charactors, sex):
		order_id = 'SO' + str(charactors) + 'D' + sex + 'T' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')[:64]
		return order_id[:31] #线下订单id


	async def prepay(self, openid, order_id, fee=0):
		try:
			res = await wxpay.WeiXinJSAPIPay(order_id, '您支付了%s' % (fee / 100), fee, openid).prepay()  #汉字就是body，这个接口（prepay）,仅仅需要四个参数openid（支付者），order_id（本地生成的线下订单号），body（点击支付时的标题提示内容），fee（支付总额）
			ctrl.web.update_namegame_order(data=dict(order_id=order_id, state=3)) #3 未支付
			IOLoop.current().add_timeout(query_delay(), self.pay_query, order_id, loop=5)
			return res

		except Exception as e:
			logging.error(e)
			raise utils.APIError(errcode=19003)

	async def pay_query(self, order_id, loop=0):
		order = ctrl.web.get_namegame_order_by_orderid(order_id)
		try:
			res = await wxpay.OrderQuery('order_id').post_xml()
		except Exception as e:
			logging.error(e)
			raise utils.APIError(errcode=10001, errmsg='查询订单失败')

		if (res['return_code'] == 'SUCCESS' and res['result_code'] == 'SUCCESS' and res['trade_state'] == 'SUCCESS'):
			ctrl.web.update_namegame_order(data=dict(order_id=order_id, state=2, wx_pay_id=res['transaction_id'])) #查询成功，才有这个线上订单id:transaction_id			res['is_pay'] = 1
			return res
		if loop > 0:
			IOLoop.current().add_timeout(delay_times(loop), self.pay_query, dict(order_id=order_id), loop=loop - 1)
		return res

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

		print(self.request.arguments)
		order_id = self.gen_order_id(charactors, sex) #订单线下id，这里没有用到erp_id，直接生成order_id
		ctrl.web.update_namegame_order(dict(order_id=order_id, openid=openid, sex=sex, charactors=charactors, fee=fee))
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
		is_pay = res['is_pay']
		return self.send_json(dict(is_pay=is_pay))


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


#微信调用，主动返回支付成功的out_trade_id
class OrderCbHandler(BaseHandler):

	@gen.coroutine
	def post(self):
		logging.info(self.request.body)
		res = wxpay.WeiXinResponse(self.request.body).verify()
		if not res:
			raise utils.APIError(errcode=10001, errmsg='验签错误')
		order_id = res['out_trade_no']
		ctrl.web.update_namegame_order(data=dict(order_id=order_id, state=2))

