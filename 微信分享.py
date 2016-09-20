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
        		title: "没文化真可怕，Angelababy已经被土哭了，快来给宝宝起个终身受益的英文名字吧！！！",
        		link: window.location.href,
        		imgUrl: "http://coupon.ktvsky.com/static/images/share.png",
        		success: function() {
        			},
       	 	cancel: function() {
        		}
   	 });
    	#分享到微信内消息
    	wx.onMenuShareAppMessage({
        		title: "没文化真可怕，Angelababy已经被土哭了，快来给宝宝起个终身受益的英文名字吧！！！",
        		desc:'我是英国Beautiful Name公司的CEO以及创始人－Monica Miller。在过去的12年，我经常到访中国。每当我在中国的时候，我经常会被同事要求帮他们和他们的孩子取一个特别的英文名。如同中文名一样，当会见朋友或工作伙伴时，他们会将英文名与您孩子的性格紧密联系在一起，同时名字也会给别人留下重要的第一印象。因此给孩子取名字不仅是极高的殊荣也是一份重大的责任。在将来，您的孩子的英文名字会出现在他们的大学申请书上，亦或是名片上。他们的名字应该代表他们希望被人记住的形象。',
        		link: window.location.href,
        		imgUrl: "http://coupon.ktvsky.com/static/getName/images/share.png",
       		type: "link",
        		dataUrl: "",
        		success: function() {
        		},
       		cancel: function() {
        		}
    }	);
});