
#/wx/custom/send:
class FiveColorHandler(BaseHandler):
	def get(self):
		self.write(self.get_argument('echostr'))

	async def post(self):
		msg = self.request.body
		msg_dict = json.loads(xml2json.xml2json(msg.decode(), optparse.Values({'pretty': True})))
		logging.error(msg_dict)
		msg_dict = msg_dict.get('xml', {})

		event = msg_dict.get('Event', '')
		openid = msg_dict.get('ToUserName', '')
		create_time = msg_dict.get('CreateTime')
		query_info = msg_dict.get('Content','')
		if event == 'SCAN':
			send_info = 'input your text!'
			openid = msg_dict.get('FormUserName')

		send_info = ctrl.get_send_info(query_info) #查询数据库

		if msgtype = 'text':
			data = dict(toopenid=openid, msgtype='text', text=dict(content=send_info))

		#获取access_token
		http_client = utils.get_async_client()
		try:
			url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}'.format(  
				appid=conf['APPID'], secret=conf['APPSECRET'])
			response = yield http_client.fetch(url, connect_timeout=20, request_timeout=20)  #get请求的写法
			r = json.loads(response.body.decode())
			logging.info(r)
			access_token = r['access_token'] #获取access_token
		except Exception as e:
			logging.error(e)
			raise utils.APIError(errcode=10001, errmsg='获取access失败')

		#由access_token调用微信接口发送信息
            		http_client = utils.get_async_client()
		try:
			request = httpclient.HTTPRequest(
				'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=%s'%access_token,
				method='POST',
				headers={'content-type': 'application/json'},
				body=json.dumps(data, ensure_ascii=False).encode(),
				connect_timeout=2,
				request_timeout=3)
			response = yield utils.fetch(http_client, request)  #post请求方式
			r = json.loads(response.body.decode())
			logging.info(r)
			return r
		except Exception as e:
			logging.error(e)
			raise utils.API(errcode=10001, errmsg='参数错') 



