class OrderHandler(BaseHandler):

	async def prepay(self, openid, erp_id, ktv_id, fee):
		try:
			other={
				#附加信息
			}
			params = {
				"tp": "", #有值就需要特殊分成
				"op": "fastpay",
				"ktvid": ktv_id,
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

			r = await utils.fetch(http_client, request)
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
				order['wx_pay_id'] = res['transaction_id']
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
			erp_id = self.get_argument('erp_id')
		except Exception as e:
			logging.error(e)
			raise utils.APIError(errcode=10001)
		order = ctrl.web.get_namegame_order_by_erp_id(erp_id)
		res = await self.pay_query(order['order_id'])
        		is_pay = res['is_pay']
        		return self.send_json(dict(is_pay=is_pay))

class AferPayHandler(BaseHandler):
	#如果查询订单is_pay=1,支付成功
    	def get(self):
	        	try:
	            		erp_id = self.get_argument('erp_id')
	        	except Exception as e:
	            		logging.error(e)
	            		raise utils.APIError(errcode=10001)

		order = ctrl.web.get_namegame_order_by_erp_id(order_id)
		gender = order['sex']
		names_info = ctrl.web.get_names_info(gender)
		names_info = random.sample(names_info, 5)
		return self.send_json(dict(names_info=names_info))