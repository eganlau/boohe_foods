# boohe_foods

获取减肥食物信息

![image.png](https://i.loli.net/2019/11/21/bDJSWKmuOh1rVQZ.png)

## build step

```
# install pipenv environment
$ pip3 install pipenv

# install module for enter project directory 
$ pipenv install

# run script
$ python3 main.py

# 没有优化线程/进程 总体抓取5.1w条数据  耗时2～3H
```
## Forking Enhancements

Based on the API info at https://www.cnblogs.com/cekong/p/11131333.html:

- Added additional v2 script to use v2 endpoint for recipe which has more complete info. 
- Scrapying the food ranking list data is also added. 

Other code enhancements include:

- Use retying library to make http request more robust.
- Use "code" field as the unique ID rather than ID field. It can lead to a more  complete record downlaods.
