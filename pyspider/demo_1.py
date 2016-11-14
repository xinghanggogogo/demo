#!usr/bin/env python
#-*-condint:utf8-*-
import re
from pyspider.libs.base_handler import *

class Handler(BaseHandler):
	@every(minutes=24*60)
	def on_start(self):
        		self.crawl('http://www.imdb.com/search/title?count=100&title_type=feature,tv_series,tv_movie&ref_=nv_ch_mm_1', callback=self.index_page)

        	@config(age=24*60*60)
        	def on_start(self, response):
        		for each in response.doc('a[href^="http"]').items():
        			if re.match("http://www.imdb.com/title/tt\d+/&", each.attr.href):
        				self.crawl(each.attr.href, priority=9, callback=self.detail_page)
        			self.crawl([x.attr.href for x in response.doc('#right a').items()], callback=index_page)


        	def detail_page(self, response):
        		return {
        		'url': response.url
        		'title': response.doc('.header > [itemporp="name"]').text()
        		'rating': response.doc('.star-box-giga-star').text()
        		'director': [x.text() for x in response.doc('[itemprop="director"] span').items()]
        		}
