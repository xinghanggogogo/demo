# -*- coding: utf-8 -*-
__author__ = 'xinghang'

import  sys
reload(sys)
sys.setdefaultencoding('utf8')
from scrapy.spiders import Spider
from scrapy.selector import Selector
import traceback
from demo.items.newsItem import *
from demo.pipelines.stat import *
from scrapy.http import Request



class techsir2Sipder(Spider):
    name = "moduo"
    download_delay = 3
    allowed_domains = ["moduovr.com"]
    start_urls = ['http://www.moduovr.com/'] #系统自动调用的。

    print '**********', start_urls

    def parse(self, response):
        print "*****************************************************"
        print response.url
        print "*****************************************************"
        staturltotal()

        sel = Selector(response)

        try:
            lis = sel.xpath('//ul[@class="list-group-article layout-row"]/article')
            for li in lis.xpath('.//div[@class="caption"]'):
                try:
                    title = li.xpath('a/h1/text()').extract()[0].encode('utf8')
                except Exception,e:
                    title=''
                    print traceback.print_exc()

                try:
                    link = li.xpath('a/@href').extract()[0].encode('utf8')
                except Exception,e:
                    link=''
                    print traceback.print_exc()

                try:
                    description = li.xpath('div[1]/text()').extract()[0].strip().encode('utf8')
                except Exception,e:
                    description=''
                    print traceback.print_exc()

                yield Request(url=link, dont_filter=True, callback=self.parse2,
                                  meta={'title': title, 'description': description,
                                        'link': link})
                # print '标题： ' + title
        except Exception, e:
            print traceback.print_exc()

    def parse2(self, response):
        staturltotal()
        # print '***************parse2', response.body


        # import time
        # time.sleep(100)
        title = response.meta.get('title')
        description = response.meta.get('description')
        link = response.meta.get('link')
        sel = Selector(response)
        try:

            datetime1 = sel.xpath('//section[@class="panel-article page-article-detail article-action hidden-xs"]/div[1]/div[1]/div[1]/div[1]/span/text()').extract()
            datetime=datetime1[1].strip().encode('utf8')
        except Exception, e:
            datetime = ''
            print traceback.print_exc()

        print '标题： '+title
        print '描述： '+description
        print '链接： '+link
        print '时间： '+datetime+':00'

        item = yiounewsItem()
        item['title'] = title
        item['description'] = description
        item['datetime'] = datetime
        item['link'] = link
        item['source'] = '魔多 - 首页'

        statitemtotal()
        yield item
# except IndexError:
    # pass


            ename = response.meta.get('ename')
            gender= response.meta.get('gender')
            sounce = response.meta.get('sounce')
            cname = response.meta.get('canme')
            source = response.meta.get('source')
            hot_level = response.meta.get('hot_level')
            detail_link = response.meta.get('detail_link')


                    print ename
                    print gender
                    print sounce
                    print cname
                    print source
                    print hot_level
                    print detail_link
                    print detail
                    print master

                    # item = nameItem()
                    # item['ename'] = ename
                    # item['gender'] = gender
                    # item['sounce'] = sounce
                    # item['cname'] = cname
                    # item['source'] = source
                    # item['hot_level'] = hot_level
                    # item['detail_link'] = detail_link

                    #statitemtotal()
                    #yield item

                    