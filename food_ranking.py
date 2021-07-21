# coding=utf-8

import pymongo,requests,random,datetime
import sys

from retrying import retry

class Db:
  def __init__(self,**conf):
    self.client = pymongo.MongoClient(**conf)

  def getDatabase(self,name):
    return self.client[name]

class BooheFoodRanking:

    @retry(wait_random_min=1000, wait_random_max=2000)
    def request(self,url):
        headers = [
            {'User-agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Mobile Safari/537.36'},
            {'User-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'},
            {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36'},
            {'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20120101 Firefox/33.0'},
        ]
        content = requests.get(url, headers=random.choice(headers))
        return content.json()
        

    def categories(self):
        """分类数据列表
        """
        content = self.request('https://food.boohee.com/fb/v1/food_rankings')
        if content['total_pages']:
            for i in range(1, content['total_pages'] + 1):
                url = "https://food.boohee.com/fb/v1/food_rankings?page=%d" % i
                content = self.request(url)
                if content["records"]:
                    for record in content["records"]:
                        data = (record["id"],record["image_url"],record["reads_count"])
                        yield data

    def ranks(self, collection):
        """食物基本信息
        """
        categories_list = self.categories()
        for i in categories_list:
            url = 'https://food.boohee.com/fb/v1/food_rankings/%d.json' % i[0]
            content = self.request(url)
            if not content['foods']:
                break
            content["image_url"] = i[1]
            content["reads_count"] = i[2]
            yield content
    
if __name__ == "__main__":
    start = datetime.datetime.now()

    mDb = Db(**{'host':'localhost', 'port':27017}) # todo
    mBooHe = BooheFoodRanking()

    db = mDb.getDatabase('boohe_food')
    collection = db.get_collection('food_ranking')
    # create index 
    collection.create_index([("title", pymongo.DESCENDING)],unique=True) 
    # collection.create_index([("name", pymongo.TEXT)])  # mongodb的中文索引简直不能用  倒不如来的慢的正则全文检索

    num = 0
    for rank in  mBooHe.ranks(collection):
        if not collection.count_documents({'title': rank["title"]}): # 不存在数据
            print("new addition to food_ranking collection:",rank["title"])
            rel = collection.insert_one(rank)
            if rel:
                num += 1
            else:
                print("insert error:",rank["title"])
        else:
            print("in collection:",rank["title"])

    end = datetime.datetime.now()
    
    print('total insert: %d time: %s' % (num,end-start))
