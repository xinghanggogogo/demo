var app = getApp()
Page({
	data:{
		originData: {},
		bookList: []
	},
	onLoad:function(options){
		var self = this;
		console.log()
		wx.request({
				url:'xxxxxxxx',
				header: {
						'Content-Type': 'application/json'
				},
				success: function(res) {
					 if(res.data.status.code == 0){
							self.handleResponse(res.data.data);
					 }
				}
		});
		console.log('onLoad')
	},

	handleResponse:function(response){
		console.log(response);
		
		var bookList = response.content.column_data;
		
		this.setData({
			originData:response,
			bookList:bookList
		});
	}
})
-------------------------------------------------
var app = getApp()
Page({
	data: {
		bookList: []
	},

	onLoat:function(){
		var that = this;
		wx.request({
			url: '***',
			headers: {
				'Content-Type': 'application/json'
			},
			success:function(res){
				if(res.data.status.code == 0){
					that.callBackFunction(res.data.data)
				}
			}
		}),
		console.log('onLoad')
	},

	callBackFunction:function(res){
		console.log(res)
		var bookList = response.content.bookList
		this.setData({
			bookList:bookList
		})
	}
})
//流程：data-onLoad-request-success-callback-setData