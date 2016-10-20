有些网站需要登录后才能访问某个页面，在登录之前，你想抓取某个页面内容是不允许的
利用Urllib2库保存我们登录的Cookie，然后再抓取其他页面就达到目的了

1.利用cookieJar保存cookie：
import urllib2
import cookielib

cookie = cookielib.CookieJar()
handler=urllib2.HTTPCookieProcessor(cookie)
opener = urllib2.build_opener(handler)
response = opener.open('http://www.baidu.com')

for item in cookie:
    print 'Name = '+item.name
    print 'Value = '+item.value

2.利用文件保存cookie：
import cookielib
import urllib2

filename = 'cookie.txt'		#同级目录下
cookie = cookielib.MozillaCookieJar(filename)
handler = urllib2.HTTPCookieProcessor(cookie)
opener = urllib2.build_opener(handler)
response = opener.open("http://www.baidu.com")
cookie.save(ignore_discard=True, ignore_expires=True)		#ignore_expires:覆盖写入

cookie = cookielib.MozillaCookieJar()
cookie.load('cookie.txt', ignore_discard=True, ignore_expires=True)
req = urllib2.Request("http://www.baidu.com")
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
response = opener.open(req)
print response.read()

3.一个例子：
import urllib
import urllib2
import cookielib

filename = 'cookie.txt'
cookie = cookielib.MozillaCookieJar(filename)
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
postdata = urllib.urlencode({
			'stuid':'201200131012',
			'pwd':'23342321'
		})
loginUrl = 'http://jwxt.sdu.edu.cn:7890/pls/wwwbks/bks_login2.login'
result = opener.open(loginUrl,postdata)
cookie.save(ignore_discard=True, ignore_expires=True)
gradeUrl = 'http://jwxt.sdu.edu.cn:7890/pls/wwwbks/bkscjcx.curscopre'
result = opener.open(gradeUrl)		#cookie之前已经存储成功
print result.read()