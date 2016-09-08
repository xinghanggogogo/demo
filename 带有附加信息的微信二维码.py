class FetchQrcodeHandler(BaseHandler):
	async def get(self):
		try:
			ktv_id = self.get_argument('ktv_id')
			username = self.get_argument('username')
		except Exception, e:
			loggint.error(e)
			raise APIError(errcode = 10001) #附加错误信息
		try:
			access_token = await utils.async_common_api('/wx/token', dict(flag=1)) #flag与公众号开发账号相关
			access_token = access_token['access_token']
			url = QRCODE_TICKET.format(access_token=access_token) #根据令牌（已经包含了唯一的公众号信息）去获取微信附带信息二维码的生成url
			params = dict(action_name='QR_LIMIT_STR_SCENE', expire_seconds=36000, action_info=dict(scene=dict(scene_str='%s,%s')%(ktv_id, client_id)))
			http_client = utils.get_async_client()
			request = utils.http_request(url, method=POST, body=json.dumps(params))
			response = await http_client.fetch(request)
			response = json.loads('response.body.decode()')
			return self.send_json({'url':response['url']})
			#这里返回的是url，形如
		except Exception as e:
			logging.error(e)
			raise APIError(errcode = 10001)

#下一步是微信公众号平台登记的 你所指定的url的Handler：
class WxCallBackHandler(BaseHandler):
	def get(self):
		self.write(self.get_argument('echostr'))

	async def post(self):
		msg = self.request.body
		msg_dict = json.loads(xml2json.xml2json(msg.decode(), optparse.Value({'pretty':True})))
		msg_dict = msg_dict.get('xml', {})
		logging.error(msg_dict)

		event = msg_dict.get('Event', '')
		openid = msg_dict.get('FromUserName'，'')
		username_and_ktv_id = msg_dict.get('EvenKey', '')
		username, ktv_id = list(map(int, username_and_ktv_id.split(',')))

		if event not in ('subsctibe', 'SCAN') or not username or not  ktv_id:
			return
		user = ctrl.pay.get_ktv_account(username)
		if  not user:
			username = int(usename)
			password_org = random.randint(99999, 100000)
			content = "短信内容" % userame, password_org
			msg = await ctrl.pay.send_message_ctl(username=username, password_org=password_org, ktv_id=ktv_id)
			if msg['type'] = 2:
				return
		await utils.async_common_api('/wx/custom/send', dict(openid=openid, text='https://erp.ktvsky.com/ktv_fin_curdata'))

