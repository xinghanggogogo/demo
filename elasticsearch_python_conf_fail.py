elasticsearch需要java环境 安装java1.8：
	$ sudo add-apt-repository ppa:webupd8team/java
	$ sudo apt-get update
	$ sudo apt-get install oracle-java8-installer
	$ java -version
下载elasticsearch并解压：
	wget https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-2.3.4.zip
下载elasticsearch-jdbc并解压：
	wget http://xbib.org/repository/org/xbib/elasticsearch/importer/elasticsearch-jdbc/2.3.4.0/elasticsearch-jdbc-2.3.4.0-dist.zip
启动：
	ubuntu：bin/elasticsearch
	centos：/etc/init.d/elasticsearch
检查：
	curl localhost:9200

------------------------------------------------------------------------------
内容已经过期！fuck
创建一个jdbc_river：
curl -XPUT localhost:9200/_river/jdbc/_meta -d '{	#_river，jbdc为自定义的river名
    "type" : "jdbc",
    "jdbc" : {
        "url" : "jdbc:mysql://192.168.0.172:3308/myktv",
        "user" : "mombaby",
        "password" : "098f6bcd4621d373cade4e832627b4f6",
        "sql" : "select id as \"_id\" from myktv_meta ",
        "index" : "myktv",
        "type" : "books_meta"
    }
}'
测试效果：
curl -XGET 'localhost:9200/myktv/books_meta/_search?pretty&q=text'  #依次对应上文的index和type
--------------------------------------------------------------------------------

关于suggestion：
pyes：
------------------------------------
from elasticsearch import Elasticsearch

es = Elasticsearch()
text = 'ra'	#可来源于输入
suggDoc = {
           "entity-suggest" : {	#这里已经指明了type：entity（实体）
                'text' : text,
                "completion" : {
                    "field" : "suggest"
                }
            }
        }

res = es.suggest(body=suggDoc, index="auto_sugg", params=None)	#注意这里仅仅指定了index，type隐藏在body中，“entity-suggest”
print(res)

-----------------------------------
from elasticsearch import Elasticsearch
es = Elasticsearch()

text = 'ra'
suggest_dictionary = {"my-entity-suggest" : {
                      'text' : text,
                      "completion" : {
                          "field" : "suggest"
                      }
                    }
                  }

query_dictionary = {'suggest' : suggest_dictionary}

res = es.search(
    index='auto_sugg',
    doc_type='entity',
    body=query_dictionary)
print(res)

#Make sure you have indexed each document with suggest field
	sample_entity= {
	        'id' : 'test123',
	        'name': 'Ramtin Seraj',
	        'title' : 'XYZ',    
	        "suggest" : {
	            "input": [ 'Ramtin', 'Seraj', 'XYZ'],
	            "output": "Ramtin Seraj",
	            "weight" : 34   # a prior weight 
	        }
	      }

官方文档--关于suggestion：

MAPPING:类似于定义表结构
curl -X PUT localhost:9200/music/song/_mapping -d '{
  "song" : {
        "properties" : {
            "name" : { "type" : "string" },
            "suggest" : { "type" : "completion",
                                 "analyzer" : "simple",
                                 "search_analyzer" : "simple",
                                 "payloads" : true
            }
        }
    }
}'

INDEX:插入记录
curl -X PUT 'localhost:9200/music/song/1?refresh=true' -d '{
    "name" : "Nevermind",
    "suggest" : {
        "input": [ "Nevermind", "Nirvana" ],
        "output": "Nirvana - Nevermind",
        "payload" : { "artistId" : 2321 },
        "weight" : 34
    }
}'

QUERYING:请求
curl -X POST 'localhost:9200/music/_suggest?pretty' -d '{
    "song-suggest" : {
        "text" : "n",
        "completion" : {
            "field" : "suggest"
        }
    }
}'

RETURN:返回
{
  "_shards" : {
    "total" : 5,
    "successful" : 5,
    "failed" : 0
  },
  "song-suggest" : [ {
    "text" : "n",
    "offset" : 0,
    "length" : 1,
    "options" : [ {
      "text" : "Nirvana - Nevermind",
      "score" : 34.0, "payload" : {"artistId":2321}
    } ]
  } ]
}

#!/bin/sh

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
bin=${DIR}/../bin
lib=${DIR}/../lib

echo '
{
"type" : "jdbc",
"jdbc" : {
"url" : "jdbc:mysql://192.168.0.172:3306/myktv",
"user" : "mombaby",
"password" : "098f6bcd4621d373cade4e832627b4f6",
"sql" : "select id as _id, books_meta.name as \"name\", books_meta.auth»
"index" : "ebook",
"type" : "ebook",
}
}
' | java \
-cp "${lib}/*" \
-Dlog4j.configurationFile=${bin}/log4j2.xml \
org.xbib.tools.Runner \
org.xbib.tools.JDBCImporter

&&&&&&&&&&&&&&&&&&&&&&&&
建立一个索引并且插入数据：
curl -X PUT localhost:9200/test/test/1 -d'{"name":"asdf"}'	#id=1

按照id查询：
curl localhost:9200/test/test/1
>>>{"_index":"test","_type":"test","_id":"1","_version":2,"found":true,"_source":{"name":"asdf"}}

内容查询：
curl localhost:9200/test/_search?q=a
>>>{"took":347,"timed_out":false,"_shards":{"total":5,"successful":5,"failed":0},"hits":{"total":0,"max_score":null,"hits":[]}}
curl localhost:9200/test/_search?q=asdf
>>>{"took":88,"timed_out":false,"_shards":{"total":5,"successful":5,"failed":0},"hits":{"total":1,"max_score":0.30685282,"hits":[{"_index":"test","_type":"test","_id":"1","_score":0.30685282,"_source":{"name":"asdf"}}]}}

suggestion查询：
注意：这里的index和type之前已经存在
建立索引结构：
curl -X PUT localhost:9200/test/test/_mapping -d '{
  "test" : {
        "properties" : {
            "name" : { "type" : "string" },
            "suggest" : { "type" : "completion",
                                 "analyzer" : "simple",
                                 "search_analyzer" : "simple",
                                 "payloads" : true
            }
        }
    }
}'
>>>{"acknowledged":true}
插入数据：
curl -X PUT 'localhost:9200/test/test/2?refresh=true' -d '{
    "name" : "Nevermind",
    "suggest" : {
        "input": [ "Nevermind", "Nirvana" ],
        "output": "Nirvana - Nevermind",
        "weight" : 100
    }
}'
>>>{"_index":"test","_type":"test","_id":"2","_version":1,"_shards":{"total":2,"successful":1,"failed":0}
请求：
curl -X POST 'localhost:9200/test/_suggest?pretty' -d '{
    "test-suggest" : {
        "text" : "ne",
        "completion" : {
            "field" : "suggest"
        }
    }
}'
返回suggestion：
{
  "_shards" : {
    "total" : 5,
    "successful" : 5,
    "failed" : 0
  },
  "test-suggest" : [ {
    "text" : "n",
    "offset" : 0,
    "length" : 1,
    "options" : [ {
      "text" : "Nirvana - Nevermind",
      "score" : 100.0
    } ]
  } ]
}

curl -X PUT localhost:9200/test1/test_suggest/_mapping -d '{
  "test" : {
        "properties" : {
            "name" : { "type" : "string" },
            "suggest" : { "type" : "completion",
                                 "analyzer" : "simple",
                                 "search_analyzer" : "simple",
                                 "payloads" : true
            }
        }
    }
}'
>>>exception

&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

真·初始化
建立一个默认配置的索引：
curl -X PUT localhost:9200/asdfasdf -d'{}'
>>>{"acknowledged":true}
定义索引内部type结构：
curl -X PUT localhost:9200/asdfasdf/_mapping/asdfasdf?pretty -d '{
         "properties":{
                   "name":{"type":"string"},
                   "published":{"type":"string"},
	     "suggest" : {
	     	 "type" : "completion",
	     	"analyzer" : "simple",
	     	"search_analyzer" : "simple",
	     	"payloads" : true
            }
         }
}'
插入数据：
curl -X PUT 'localhost:9200/asdfasdf/asdfasdf/1?refresh=true' -d '{
    "name" : "xinghang",
    "published": "南京",
    "suggest" : {
        "input": [ "xinghang", "wenyi", "nanjing" ],
        "output": "xinghang",
        "weight" : 100
    }
}'
>>>{"_index":"asdfasdf","_type":"asdfasdf","_id":"1","_version":1,"_shards":{"total":2,"successful":1,"failed":0},"created":true}

curl -X PUT 'localhost:9200/asdfasdf/asdfasdf/1?refresh=true' -d '{
    "name" : "xinghang_1",
    "published": "nanjing",
    "suggest" : {
        "input": [ "xinghang", "wenyi", "nanjing" ],
        "output": "xinghang",
        "weight" : 100
    }
}'

按照id查询：
curl localhost:9200/asdfasdf/asdfasdf/1
>>>
{"_index":"asdfasdf","_type":"asdfasdf","_id":"1","_version":1,"found":true,"_source":{
    "name" : "xinghang",
    "published": "南京",
    "suggest" : {
        "input": [ "xinghang", "wenyi", "nanjing" ],
        "output": "xinghang",
        "weight" : 100
    }
}}

按照内容查询（完全匹配任意字段）：
curl localhost:9200/asdfasdf/_search?q=南京	#无法直接识别中文
>>>fail！！！
curl localhost:9200/asdfasdf/_search?q=xinghang
>>>success
curl localhost:9200/asdfasdf/_search?q=nanjing
>>>success

suggest查询：
curl -X POST 'localhost:9200/asdfasdf/_suggest?pretty' -d '{
    "test-suggest" : {
        "text" : "x",		#"xinghang","nan","weny"都成功了
        "completion" : {
            "field" : "suggest"
        }
    }
}'
>>>{
  "_shards" : {
    "total" : 5,
    "successful" : 5,
    "failed" : 0
  },
  "test-suggest" : [ {
    "text" : "weny",
    "offset" : 0,
    "length" : 4,
    "options" : [ {
      "text" : "xinghang",
      "score" : 100.0
    } ]
  } ]
}
