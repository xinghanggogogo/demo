1.handler:
@get_user_info
class xxx():

2.decrator:
def get_user_info(func):
	def wrap(*args, **kw):
		self = arg[0]
		openid = self.get_cookie('openid')
		pprint('openid:%s' % openid)
		if not openid:
			url = WX_GET_USERINFO_CODE.format(   #需要一个appid，回调处理code的url，请求的state
					appid = yourappid,
					redirect_uri = quote(yourhandlecodeurl)
					state = quote(self.request.path)
				)
			retutn self.redirect(url)    #请求这个url的时候会带上code和上文的state
		return func(*args, **kw)
	return wrap
3.handler:

class yourhandlercodeurlHandler(BaseHandler):

	def get_user_info(self,code):
		key = 'wx_user_%s' % code
		if ctrl.rs.exist(key):
			return eval(ctrl.rs.get(key))
		http_client = utils.get_async_client()
		try:
			url = 'https://api.weixin.qq.com/sns/oauth2/access_token'
			params = {
				'appid':yourappid,
				'secret':yourappsecret,
				'code':code,
				'grant_type':'authorization_code'
			}
			response = await http_client.fetch(url_concat(url, params), connect_time=20, request_timeout=20)
			response = json.loads(response.body.decode())
			user_info = ctrl.pay.get_user_info_by_openid_ctl(r['openid'])
			if user_info:
				ctrl.rs.set(key, user_info, 60*10)
				return user_info
		except Exception as e:
			logging.error(e)
			raist APIError(errcode=10001, errmsg='获取access_token')
		http_client = utils.get_async_client()
		try:
			url = 'https://api.weixin.qq.com/sns/userinfo'
			params = {
				'access_token':response['access_token'],
				'openid':r['openid'],
				'lang':'zh_CN'
			}
			response = http_client.fetch(url_concat(url, params), connect_time=10, request_timeout=10)
			user_info = json.loads(response.body.decode())
			ctrl.rs.set(key, user_info, 60*10)
			ctrl.pay.add_user(openid = openid, nickname = nickname, headimgurl=,headimgurl)
			return user_info
		except Exception as e:
			logging.error(e)
			raise utils.APIError(errcode=10001, errmsg='获取用户信息失败')

4.#微信的回调函数，获取code
	def get(self):
		try:
			code = self.get_argument('code')
			state = self.get_argument('state')  #请求微信验证的起始地址
		except Exception as e:
			logging.error(e)
			raise APIError(errcode=10001)

		#此时必然已经有了code:
	       user_info = async self.get_user_info(code)
		logging.info('user: %s' % user_info)
		self.set_cookie('openid': user_info['openid'])
		return self.redirect(uniquote(state))
		






