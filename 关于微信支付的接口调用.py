class OrderHandler(BaseHandler):

	def gen_order_id(sopenid, dopenid, fee):
		return sopenid + 'SO' + str(fee) + 'D' + dopenid + 'T' +datetime.datetime.now().strftime('%Y%m%d')

	async def prepay(self, ktv_id, openid, order_id, pay_fee, real_fee=0):
		try:
			params = {
				"op":"fastpay" ,#weixindefault 
				"ktv_id":ktv_id,
				"erpid":order_id,
				"action":json_dumps({
					'paramsBody':'nidashangle %.02f' % (pay_fee / 100),
					'paramsTotalFee':pay_fee,
					'paraOpenId': openid,
					})
			loggin.error('prepay params: %s' % params)

			url = 'http://pay.ktvsky.com/wx'
			http_client = utils.get_async_client()
			request = httpclient.HTTPRequest(url_concat(url, params), method='POST', body=' ', headers={}, connect_time=10, request_timeout=10 )
			r = await utils.fetch(http_client, request)
			r = json.loads(bytes(r.body).decode())
			logging.error(r)

			ctrl.web.update_by_order(order_id, data=dict(state=3, wx_pay_id=r['order']))
			IOloop.current().add_timeout(query_delay(), self.pay_query, order_id, loop=5) # 5times to dedect the pay result
			
			return r
		except Exception as e:
			logging.error(e)
			raise utils.APIError(errcode=19003)
			}

	async def  pay_query(self, order_id, loop=1): #chaxundingdanshifouzhifuchenggong 
		logging.info("\n\n loop%s" % loop)

		order = ctrl.web.get_by_order_with_id(order_id)
		if not order:
			raise utils.APIError(errcode=10001)
		try:
			params = {
				"op": "query",
				"ktvid":BY_KTV_ID,
				"paytype": "wx",
				"data":json_dumps({
					"paraOutTradeNo":order['wx_pay_id']
					})
				}
			url = 'http://pay.ktvsky.com/wx'
			http_client = utils.get_async_client()
			request = httpclient.HTTPRequest(url_concat(url, params), method='POST', body=' ', headers={}, connect_time=10, request_timeout=10 )
			r = await utils.fetch(http_client, request)
			r = json.loads(bytes(r.body).decode())
			logging.error(r)

			if utils.is_success_pay('wx', res):
				IOloop.current().spawn_callback(self.after_pay, order)  #houxudechuli hanshu ,lirufenxiangzhilei 

	@forbid_frequent_api_call(params={'cookie_keys':['openid'], 'seconds': 5})
	async def post(self):
		try:
			by_order_id = int(self.get_argument('id'))  #beauty_id
			by_room_id = self.get_argument('room_id')
			by_fee = self.get_argument('by_fee', 200)
		except  Exception as e:
			logging.error(e)
			raise utils.APIError(errcode = 10001)

		key = 'by_order_%s' % by_order_id  #redis
		if not ctrl.rs.setnx(key , 1):  #no exist renturn true and set key ;exist return false
			raise utils.APIError(errcode = 18001, errmsg = 'already be baoyaoed')
		ctrl.rs.expire(key, 3*60)

		copenid = self.get_cookie('openid')
		by_order = ctrl.web.get_by_order_with_id(by_order_id)
		if not by_order:
			raise utils.APIError(errcode = 18001, errmsg = 'baoyang meinv bucunzai')
		if by_order['state'] == 2:
			raise utils.APIError(errcode = 18001, errmsg = 'yijingbeiqiangzou')
		if by_order['dopenid'] == copenid:
			raise utils.APIError(errcode = 18001, errmsg = 'buyaobaoyangniziji ')
		if by_fee < by_order['fee']:
			raise utils.APIError(errcode = 18001, errmsg = 'baoyangjineyouwu')

		ktv_id = BY_KTV_ID
		order_id = gen_order_id(copenid, by_order['dopenid'], by_fee)
		ctrl.web.update_by_order_with_id(by_order_id, dict(sopenid=copenid, order_id=order_id, by_room_id=by_room_id, by_fee=by_fee))

		prepay_data = await self.prepay(ktv_id, copenid, order_id, by_fee, by_order['fee'])
		logging.error(prepay_data)
		res = dict(oid=order_id, pay=prepay_data)
		self.send_json(res)

	def get(self): #qianduanzhifuhou,youqianduanzhudonglaidiaochaxundingdanshifouchenggong
		try:
			order_id = self.get_argument('order_id')
		except Exception as e:
			logging.error(e)
			raist util.APIError(errcode=10001)
		res = await self.pay_query(order_id)  #chaxundingdanshifouzhifuchenggong
		is_pay = 1 if utils.is_success_pay('wx', res) else 0
		if is_pay:
			by_order = ctrl.web.get_by_order(order_id)
			room_id, contract, nickname = by_order
			return self.send_json(dict(is_pay=is_pay, room_id=room_id, contract=contract, nickname=nickname))
