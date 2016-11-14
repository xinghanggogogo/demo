#微信用户信息请求的返回    
{
	"subscribe": 1, 
	"openid": "o6_bmjrPTlm6_2sgVt7hMZOPfL2M", 
	"nickname": "Band", 
	"sex": 1, 
	"language": "zh_CN", 
	"city": "广州", 
	"province": "广东", 
	"country": "中国", 
	"headimgurl":    "http://wx.qlogo.cn/mmopen/g3MonUZtNHkdmzicIlibx6iaFqAc56vxLSUfpb6n5WKSYVY0ChQKkiaJSgQ1dZuTOgvLLrhJbERQQ4eMsv84eavHiaiceqxibJxCfHe/0", 
	 "subscribe_time": 1382694957,
	 "unionid": " o6_bmasdasdsad6_2sgVt7hMZOPfL"
	 "remark": "",
	 "groupid": 0
}
#redis的使用，key，value为list，set函数，get函数，eval函数的使用
key = 'namegame_%s' % openid
if ctrl.rs.exists(key):
		names_info = eval(ctrl.rs.get(key))
		self.send_json(dict(names_info=names_info))

key = 'namegame_%s' % order['open_id']
ctrl.rs.set(key, names_info, 60*10)
