# coding=utf-8
"""获取薄荷健康食物信息

写入mongodb数据库 boohe_food.foods_detail_v2


接口参数：
https://github.com/ai6552254636/Foods/blob/master/app/src/main/java/lanou/foodpies/%E6%8E%A5%E5%8F%A3%E6%96%87%E4%BB%B6
https://apps.apple.com/cn/app/id918422658
https://www.cnblogs.com/cekong/p/11131333.html

食物排名：
https://food.boohee.com/fb/v1/food_rankings/12.json
"""

import pymongo,requests,random,datetime
from retrying import retry

class Db:
  def __init__(self,**conf):
    self.client = pymongo.MongoClient(**conf)

  def getDatabase(self,name):
    return self.client[name]

class BooheFood:

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
        content = self.request('http://food.boohee.com/fb/v1/categories/list')
        # rel = []
        if content['group']:
            for kind in content['group']:
                kind_name = kind['kind']
                for categories in kind['categories']:
                    # categories['name']
                    categorie_id = categories['id']
                    data = (categorie_id,categories['name'],kind_name)
                    yield data
                    # rel.append(data)
        # return rel

    def foods(self, collection):
        """食物基本信息
        """
        categories_list = self.categories()
        for i in categories_list:
            page = 1
            while True:# 处理分页
                url = 'http://food.boohee.com/fb/v1/foods?value=%d&kind=%s&page=%s' % (i[0],i[2],page)
                content = self.request(url)
                if not content['foods']:
                    break
                for food in content['foods']:
                    # food 食物基本数据 http://food.boohee.com/fb/v1/foods?value=1&kind=group&page=1
                    if not collection.count_documents({'code': food['code']}): # 不存在数据
                        rel = collection.insert_one(food)
                        print(food)
                        food_code = food['code']
                        yield food_code
                    else:
                        print("food already exists:",food['code']," id:",food['id'])
                        # print(food)
                page += 1
    
    def foods_detail(self,code):
        """食物详细信息
        可以获取更多信息
        https://ifood.boohee.com/v2/ifoods/shinikanpuyanmaimaifupian/show_with_light        https://food.boohee.com/fb/v1/foods/yumi_xian.json (比mode_show少了一些tag)
        
        Arguments:
            code {str} -- 食物对应的code名称
        """
        
        url = 'https://ifood.boohee.com/v2/ifoods/%s/show_with_light' % code
        content = self.request(url)
        if 'code' in content and code == content['code']:
        # if 'id' in content and code == content['code']:
            return content
        return None


if __name__ == "__main__":
    start = datetime.datetime.now()

    mDb = Db(**{'host':'localhost', 'port':27017}) # todo
    mBooHe = BooheFood()

    db = mDb.getDatabase('boohe_food')
    collection = db.get_collection('foods_detail_v2')
    food_collection = db.get_collection('foods')
    # create index 
    collection.create_index([("code", pymongo.DESCENDING)],unique=True) 
    # collection.create_index([("name", pymongo.TEXT)])  # mongodb的中文索引简直不能用  倒不如来的慢的正则全文检索
    food_collection.create_index([("code", pymongo.DESCENDING)],unique=True) 

    num = 0
    for food_code in  mBooHe.foods(food_collection):
        if not collection.count_documents({'code': food_code}): # 不存在数据
            print("not in food_detail_v2 collection",food_code)
            data = mBooHe.foods_detail(food_code)
            if data:
                if not collection.count_documents({'code': data['code']}): # 不存在数据
                    rel = collection.insert_one(data)
                    if rel:
                        # rel.inserted_id
                        num += 1
                else:
                    print("already in food_detail_v2 collection:",food_code)
        else:
            print("in collection:",food_code)

    end = datetime.datetime.now()
    
    print('total insert: %d time: %s' % (num,end-start))
