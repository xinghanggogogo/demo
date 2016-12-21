//全局AJAX事件处理程序------------------------------

$(document).ajaxSend(function(event, xhr, settings) {
	/* stuff to do before an AJAX request is sent */;
});
$(document).ajaxStart(function() {
	/* Stuff to do when an AJAX call is started and no other AJAX calls are in progress */;
});
$(document).ajaxStop((function() {
	/* stuff to do when all AJAX calls have completed */;
});
$(document).ajaxSuccess(function(event, xhr, settings) {
	/* executes whenever an AJAX request completes successfully */
});
$(document).ajaxComplete(function(event, xhr, settings) {
	/* executes whenever an AJAX request completes */
});
$(document).ajaxError(function(event, xhr, settings, thrownError) {
	/* Stuff to do when an AJAX call returns an error */;
});

//AJAX辅助方法------------------------------

//将一个object转化为url参数
var params = {a:3; b:4}
new_params = $.param(params)
//将一个form表单提交内容转化为url参数
var new_params = $("form").serialize()
//将一个form表单的提交内容转化为一个array
$('form').submit(function(){
	console.log($(this).serializeArray())	//[{}, {}]
})

//AJAX底层接口------------------------------

$.ajax({
	url: '/path/to/file',
	type: 'default GET (Other values: POST)',
	dataType: 'default: Intelligent Guess (Other values: xml, json, script, or html)',
	data: {param1: 'value1'},
})
.done(function() {
	console.log("success");
})
.fail(function() {
	console.log("error");
})
.always(function() {
	console.log("complete");
});

$.ajaxSetup({
	url: '/path/to/file',
	type: 'default GET (Other values: POST)',
	dataType: 'default: Intelligent Guess (Other values: xml, json, script, or html)',
	data: {param1: 'value1'},
})
.done(function() {
	console.log("success");
})
.fail(function() {
	console.log("error");
})
.always(function() {
	console.log("complete");
});

//AJAX快捷方法:

$.get('/xinghang', function(data){
	$(".result").html(data);
	console.log('get success')
})

$.getJSON('/xinghang', {param1: 'value1'}, function(data) {
	var item = [];
	$.each(data, function(key, val){
		items.push('<li id="'+key+'">val<li>')
	})
	$('<ul/>', {'class':'ul-class', html:items.join(',')}).appendTo('body')
});

$.getJSON('/xinghang', {param1: 'value1'}, function(data) {
	var item = [];
	$.each(data, function(key, val){

	});
});


$.post('/xinghang', {param1: 'value1'}, function(data) {
	console.log(data)
});

$('#result').load('xinghang.html', function(){
	//some action
})
$('#result').load('xingang/html' #container)  //只加载部分
$('#result').load(function() {
	jQuery.ajax({
		url: '/path/to/file',
		type: 'POST',
		dataType: 'xml/html/script/json/jsonp',
		data: {param1: 'value1'},
		complete: function(xhr, textStatus) {
			//called when complete
		},
		success: function(data, textStatus, xhr) {
			//called when successful
		},
		error: function(xhr, textStatus, errorThrown) {
			//called when there is an error
	  }
	});
	
});
//JQUERY属性相关------------------------------

$('p').addClass('class_name')
$('p').removeClass('class name')
$('p').last().addClass('class_name')
$('ul li:last').addClass(function(index){
	return "item"+index;
})

var p_title = $('p').attr('title')	//attr用于自定义属性
var p_title = $('p').prop('class')	//prop用于自带属性 
$('div').text(p_title)

$('div#result').append($('p').hasClass('className').ToString())

$('p').click(function(){
	$(this).text($(this).html())
})

$('p').removeAttr('attribute name')
$('p').removeProp('property name')

$('div.foo').toggleClass(function(){
	if ($(this).parent().is('.bar')){
		return 'happy'
	}else{
		return 'sad'
	}
});

$('input').keyup(function(){
	var value = $(this).val();
	$('p').text(value)
})

//JQUERY 选择器------------------------------
$('*')
$('div')
$('div#div_id')
$('div.div_class')
$('div[id]')	//所有包含id属性的div
$('form input').css('border', '9px solid red')		//后代元素
$('div:animated') 'http://www.css88.com/jqapi-1.9/animated-selector/'
$('a[hreflang |= "en"]').css('border', '3px dotted green')		//选择指定属性值等于给定字符串或以该字符串为前缀（该字符串后跟一个连字符“-” ）的元素
$('input[name*="man"]').val('some text')	//选择指定属性具有包含一个给定的子字符串的元素。（选择给定的属性是以包含某些值的元素）
$('input[name~="man"]').val('some text')	//选择指定属性用空格分隔的值中包含一个给定值的元素
$('input[name$="man"]').val('some text')	//选择指定属性是以给定值结尾的元素
$('input[name^="man"]').val('some test')	//选择指定属性是给定值的元素。
$('input[name="man"]').val('some text')	//选择指定属性是给定值的元素
$('input[name!="man"]').val('some text')	//选择不存在指定属性，或者指定的属性值不等于给定值的元素
$(':button').addClass('class_name')
$('form input:checkbox').parent().css('border', '2px dotted green')
$('input:checked').length()
$('input:disabled')
$('ul.topnavi > li').css('border'. '4px dotted green')
$('div:contains('John')').css('text-decoration', 'underline')
$("td:empty").text("Was empty!").css('background', 'rgb(255,220,200)')
$('td:eq(2)').css('color', 'red')	//第二个
$('td:gt(5)').css('color', 'red')	//所有index大于5的, 相同用法, lt
$('td:gt(-1)').css('color', 'red')	//支持倒数
$('td:even').css('color', 'red')	//even;odd
$('input:file').css('color', 'red')	//选择属性为file的的input
$('div span:first-child').css('text-decoration', 'underline').hover(function(){
	$(this).addClass('class_name'),function(){
		$(this).removeClass('class_name')
	}
})
$('div span:last-child').css('text-decoration', 'underline')
$('div span:first-of-type').addClass('class_name')
$('div:has(p)').addClass('class_name')

//JQUERY操作------------------------------

//class属性
$('').addClass('class_name')
$('').removeClass('class name')
$('').hasClass('className')
$('').toggleClass('selector')

//复制元素
$('').clone().appendTo('selector')

//DOM包裹元素,卸除包裹元素
var pTags = $('p')
$('button').click(function(){
	if (pTags.parent().is('div')){
		pTags.unwrap();
	}else{
		pTags.wrap('<div></div>')
	}
	})

//插入DOM
$('').append('some text')	//末尾插入
$('').text('some text')
$('').html()	//读取选择器元素的html
$('span').appendTo('#id')
$('p').first().after(function(){
	return '<div>'+this.className+'</div>'
})	//同before

//DOM移除替换
$('p').detach()	//删除所有p元素
$('p').remove()	//同上
$('p#id').empty() //删除选择匹配元素下的的所有子元素包含文本


