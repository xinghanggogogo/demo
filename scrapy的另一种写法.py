#爬取腾讯新闻:
import re
import json

from scrapy.selector import Selector
try:
	from scrapy.spiders import Spider
except:
	from scrapy.spiders import BaseSpider as Spider
from scrapy.utils.response import get_base_url
from scrapy.spiders import CrawlSpider, Rule#这个Rule是非常重要的一个模块
from scrapy.linkextractors import LinkExtractor as sle#这里其实就是LinkExtractor as sle

from qqnews.items import *
from misc.log import *
from misc.spider import CommonSpider

class qqnewsSpider(CommonSpider):
	name = "qqnews"
	allowed_domains = ["tencent.com", 'qq.com']
	start_urls = [
		'http://news.qq.com/society_index.shtml'
	]
	#匹配url的规则
	rules = [
		Rule(sle(allow=('society_index.shtml')), callback='parse_0', follow=True),
		Rule(sle(allow=(".*[0-9]{8}.*htm$")), callback='parse_1', follow=True),
	]
	#由样式匹配内容的规则
	list_css_rules = { 
		'.linkto': {
			'url': 'a::attr(href)',
			'name': 'a::text',
		}   
	}
	list_css_rules_2 = {
		'#listZone .Q-tpWrap': {
			'url': '.linkto::attr(href)',
			'name': '.linkto::text'
		}
	}
	#另外一种写法
	content_css_rules = {
		'text': '#Cnt-Main-Article-QQ p *::text',
		'images': '#Cnt-Main-Article-QQ img::attr(src)',
		'images-desc': '#Cnt-Main-Article-QQ div p+ p::text',
	}

	def parse_0(self, response):
		info('Parse0 '+response.url)
		x = self.parse_with_rules(response, self.list_css_rules, dict)#按照样式去解析resopnse，然后转换成dict类型
		pp.pprint(x)
		#return self.parse_with_rules(response, self.list_css_rules, qqnewsItem)

	def parse_1(self, response):
		info('Parse1 '+response.url)
		x = self.parse_with_rules(response, self.content_css_rules, dict)
		pp.pprint(x)
		#import pdb; pdb.set_trace()

	def parse_2(self, response):
		info('Parse2 '+response.url)

#爬取斗鱼TV
import re
import json
from urlparse import urlparse
import urllib
import pdb

from scrapy.selector import Selector
try:
	from scrapy.spiders import Spider
except:
	from scrapy.spiders import BaseSpider as Spider
from scrapy.utils.response import get_base_url
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor as sle

from douyu.items import *
from misc.log import *
from misc.spider import CommonSpider

class douyuSpider(CommonSpider):
	name = "douyu"
	allowed_domains = ["douyu.com"]
	start_urls = [
		"http://www.douyu.com/directory/all"
	]
	rules = [
		Rule(sle(allow=("http://www.douyu.com/directory/all")), callback='parse_1', follow=True),
	]

	list_css_rules = { 
		'#live-list-contentbox li': {
			'url': 'a::attr(href)',
			'room_name': 'a::attr(title)',
			'tag': 'span.tag.ellipsis::text',
			'people_count': '.dy-num.fr::text'
		}
	}

	list_css_rules_for_item = {
		'#live-list-contentbox li': {
			'__use': '1',
			'__list': '1',
			'url': 'a::attr(href)',
			'room_name': 'a::attr(title)',
			'tag': 'span.tag.ellipsis::text',
			'people_count': '.dy-num.fr::text'
		}
	}

	def parse_1(self, response):
		info('Parse '+response.url)
		x = self.parse_with_rules(response, self.list_css_rules_for_item, douyuItem)
		print(len(x))
		return x
		#x = self.parse_with_rules(response, self.list_css_rules, dict)
		# print(json.dumps(x, ensure_ascii=False, indent=2))
		# pp.pprint(x)
		# return self.parse_with_rules(response, self.list_css_rules, douyuItem)