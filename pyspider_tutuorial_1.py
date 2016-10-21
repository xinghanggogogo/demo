from libs.base_handler import *
import re

class Handler(BaseHandler):
	
	crawl_config = {
		"headers": {
			"User-Agent": "BaiDuSpider",
		}
	}

	def on_start(self):
		self.crawl('http://www.ncbi.nlm.nih.gov/pubmed/26028028',
				   age=0, callback=self.detail_page)
		self.crawl('http://www.ncbi.nlm.nih.gov/pubmed/?term=human+activity+recognition',
				   age=0, callback=self.index_page)
	
	def index_page(self, response):
		for each in response.doc('a').items():
			if re.match('http://www.ncbi.nlm.nih.gov/pubmed/\d+$', each.attr.href):
				self.crawl(each.attr.href, age=0, callback=self.detail_page)
		
	@config(fetch_type="js")
	def detail_page(self, response):
		self.crawl('http://www.ncbi.nlm.nih.gov/pubmed?linkname=pubmed_pubmed&from_uid=' + re.search('pubmed/(\d+)$', response.url).group(1), age=0, callback=self.index_page)
		return {
				"url": response.url,
				"title": response.doc('.rprt_all > div > h1').text(),
				"authors": [x.text() for x in response.doc('.auths').items()],
				"abstract": response.doc('.abstr > div > p').text(),
				}