实现微信分享，渲染模板加入参数config：

class OpenShareHandler(BaseHandler):
	access_token = yield ctrl.apt.get_access_token_ctrl()
	jsapi_ticket = yield ctrl.apt.get_jsapi_ticket_ctrl()
	config = {
		'nonceStr':''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))
		'jsapi_ticket':jsapi_ticket,
		'timestamp':int(time.time())
		'url':self._full_url
	}
            	urlparams = '&'.join(['%s=%s' % (key.lower(), ret[key]) for key in sorted(ret)])
	config['signature'] = sha1(urlparams.encode()).hexdigest()
	config['appId'] = WXCOF['APPID']
	self.render(
		'***.tpl',
		config = config,
		)


前端引入：
<script src="http://res.wx.qq.com/open/js/jweixin-1.0.0.js"></script>
<script "text/javascript">
	#注入配置信息
	$(function(){
		wx.config({
			appId:  "{{config.get('appId')}}",
			timestamp: "{{config.get('timestamp')}}",
			nonceStr:  "{{config.get('nonceStr')}}",
			signature:  "{{config.get('signature')}}",
			jsApiList:  ['onMenuShareTimeline', 'onMenuShareAppMessage']
			})
		}
	)


js调用：
wx.ready(function() {
	#检查接口是否注入成功
    	wx.checkJsApi({
        		jsApiList: ["onMenuShareTimeline", "onMenuShareAppMessage"]
    		);
    	#分享到朋友圈
    	wx.onMenuShareTimeline({
        		title: "分享标题",
        		link: window.location.href, #当前链接
        		imgUrl: "图片链接",
        		success: function() {
    				#成功之后回调函数
        			},
       	 	cancel: function() {
        		}
   	 });
    	#分享到微信内消息
    	wx.onMenuShareAppMessage({
        		title: "分享标题"
        		desc:'分享描述',
        		link: window.location.href,
        		imgUrl: "图片链接",
       		type: "link",
        		dataUrl: "",
        		success: function() {
        		},
       		cancel: function() {
        		}
    }	);
});