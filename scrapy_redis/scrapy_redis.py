描述：

1.使用两台机器，一台是win10，一台是centos7，分别在两台机器上部署scrapy来进行分布式抓取一个网站

2.centos7的ip地址为192.168.1.112，用来作为redis的master端，win10的机器作为slave

3.master的爬虫运行时会把提取到的url封装成request放到redis中的数据库：“dmoz:requests”，并且从该数据库中提取request后下载网页，再把网页的内容存放到redis的另一个数据库中“dmoz:items”

4.slave从master的redis中取出待抓取的request，下载完网页之后就把网页的内容发送回master的redis

5.重复上面的3和4，直到master的redis中的“dmoz:requests”数据库为空，再把master的redis中的“dmoz:items”数据库写入到mongodb中

6.master里的reids还有一个数据“dmoz:dupefilter”是用来存储抓取过的url的指纹（使用哈希函数将url运算后的结果），是防止重复抓取的
