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

from six import itervalues
import mysql.connector
from datetime import date, datetime, timedelta
    
class SQL:
    
        username = 'pyspider'   #数据库用户名
        password = 'pyspider'   #数据库密码
        database = 'result'     #数据库
        host = 'localhost'      #数据库主机地址
        connection = ''
        connect = True
    placeholder = '%s'
    
        def __init__(self):
                if self.connect:
                        SQL.connect(self)
    def escape(self,string):
        return '`%s`' % string
        def connect(self):
            config = {
                'user':SQL.username,
                'password':SQL.password,
                'host':SQL.host
            }
            if SQL.database != None:
                config['database'] = SQL.database
    
            try:
                cnx = mysql.connector.connect(**config)
                SQL.connection = cnx
                return True
            except mysql.connector.Error as err:
    
            if (err.errno == errorcode.ER_ACCESS_DENIED_ERROR):
                print "The credentials you provided are not correct."
            elif (err.errno == errorcode.ER_BAD_DB_ERROR):
                print "The database you provided does not exist."
            else:
                print "Something went wrong: " , err
            return False
    
    
    def replace(self,tablename=None,**values):
        if SQL.connection == '':
                    print "Please connect first"
                    return False
    
                tablename = self.escape(tablename )
                if values:
                        _keys = ", ".join(self.escape(k) for k in values)
                        _values = ", ".join([self.placeholder, ] * len(values))
                        sql_query = "REPLACE INTO %s (%s) VALUES (%s)" % (tablename, _keys, _values)
                else:
                        sql_query = "REPLACE INTO %s DEFAULT VALUES" % tablename
    
                    
        cur = SQL.connection.cursor()
                try:
                    if values:
                            cur.execute(sql_query, list(itervalues(values)))
                    else:
                            cur.execute(sql_query)
                    SQL.connection.commit()
                    return True
                except mysql.connector.Error as err:
                    print ("An error occured: {}".format(err))
                    return False


sheet_dict.setdefault('data', []).append([result['title'], result['singer'], result['lang'], result['格式']])
