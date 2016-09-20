#http://pay.ktvsky.com/wx
class OrderHandler(BaseHandler):

	def generate_order_id(order_data):
	    	ktvid = order_data['ktv_id']
	    	prefix = BILL_TAG if not order_data['is_gzh'] else BILL_TAG+'GZH'
	    	if options.debug or str(ktvid) == '84579':
	        	prefix = 'off' + prefix
	   	 order_id = prefix+str(ktvid) + 'T' + datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
	   	 return order_id[:31]

	@gen.coroutine
	def get_pay_getorder(self, data):
		order_id = self.gennerate_order_id(data)
		try:
			try:
				total_fee = int(float(self.get_argument('fee'))*100)
			except:
				#快速下单
				total_fee = int(data['paraTotalFee'])
			ktv_id = self.get_argument('ktvid')
			ktv = ctrl.api.get_ktv_ctl(ktv_id)
			assert ktv
		except:
			raise utils.APIError(errcode = 10001, errmsg = '参数不和法')

		ctrl.api.add_wxorder(
				ktv_id = ktv_id,
		            	erp_id=self.get_argument('erpid', ''),
			      erp_date=self.get_argument('date', '').replace('/', '-'),
				remark=self.get_argument('mark', ''),
				other=self.get_argument('other', ''),
				total_fee=total_fee,
				rate_fee=utils.calc_rate(total_fee, ktv, WXCONF),
				rt_rate_fee=utils.calc_rt_rate(total_fee, ktv, WXCONF),
				order_id=order_id
			)
             return dict(order=order_id, type=2, coupon_fee=0,coupon_detail='')

       @gen.coroutine
       def post_pay(self):
       	order_id = data['order_id']
       	action = data['action'].lower
       	order = get_order(order_id)
       	if (not order or 
       		order['state'] != OrderState['CREATED'] or
       		order['total_fee'] = int(data['paramTotalFee']) or 
       		action not in ('sweep', 'micropay', 'gzh')
       		):
       		raise utils.APIError(errcode=10001, errmsg='订单id错误或者已经下下单或者金额出错')
		new_order = dict(
				order_id = order_id,
				action = DB_ACTION[action],
				body=data['paraBody'],
				dogname=data['dogname'],
				ktv_id=data['ktv_id'],
				coupon_send_id=data['coupon_send_id'],
				coupon_value=data['coupon_value'],
				c_openid=data['c_openid'],
				c_staffname=data['c_staffname'],				
			)       		
		if res['retunr_code'] == 'SUCCESS' and res['result_code'] == 'SUCCESS':
			new_order.updata(
					dict(wx_pay_id=res['transaction_id'], state=OrderState['PAYED']) if 'transaction_id' in res else dict (state=OrderState['UNPAY'])
				)
			IOloop.current().add_timeout(delay_times(), self.post_query, dict(order_id=order_id), MAX_LOOP)
		ctrl.api.update_wxorder(**new_order)
		return  res

	@gen.coroutine
	def post_fastpay(self, data):
		order = yield self.get_pay_getorder(data)
		data['order_id'] = order['order']
		wx_order = yield self.post_pay(data)
		wx_order.update(order)
		ctrl.rs.set(key, json.dumps(wx_order), 60*10)
		return wx_order

	@gen.coroutine
	def post(self):
		yield self.route_api()
		return

	def route_api(self, method='post'):
		func = method.lower()+'_'+self.get_argument('op', '')
		print ('func ==>%s' % func)	
		if hasattr(self, func):
			data = self.check_args()
			res = yield getattr(self, func)(data)
			[res.pop(o) for o in ('appid', 'mch_id', 'sub_appid, 'sub_mch_id) if o in res]
			self.send_json(res)
		else:
			raise utils.APIError(errcode = 10001, errmsg='接口不存在')
