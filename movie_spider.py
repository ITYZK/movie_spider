#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import time,pymongo
import queue,os
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

class Spdier():
    q = queue.Queue()
    def __init__(self,url):
        self.cnn = pymongo.MongoClient('mongodb://localhost:27017/')
        self.db = self.cnn['movie']
        self.url = url

    def get_name(self):
        self.driver = webdriver.Firefox()
        self.driver.get(self.url)
        html = self.driver.page_source
        html = etree.HTML(html)
        root = html.xpath('//div[@class="co_area2"]')
        for i in root[:4]:
            title = i.xpath('./div[@class="title_all"]/p/span//text()')
            
            print(title[0].strip())
            movies_url = i.xpath('./div[@class="co_content222"]/ul/li')
            for j in movies_url:
                name = j.xpath('./a//text()')
                url = j.xpath('./a/@href')
                name = name[0].strip().replace('.','_')
                url = url[0]
                print(name,url)
                self.q.put((name,url))
            self.get_download_url(title[0].strip())
            print(title[0].strip()+'is over.......\n\n')

    def get_download_url(self,title):
        data = {}
        while not self.q.empty():
            name,download_url = self.q.get()
            res = requests.get(self.url + download_url).text
            html = etree.HTML(res)
            load_url = html.xpath('//div[@id="Zoom"]/table/tbody/tr/td/a/@href')
            
            if not load_url:
               continue
            
            data[name] = load_url
        self.save(title,data)

    def save(self,title,data):
        self.cur = self.db[title] #创建相应的集合
        self.cur.insert(data)       #插入文档

    def show(self):
        movie_type = self.db.list_collection_names()    #查看所有的集合
        type_cnt = len(movie_type)
        for i in range(type_cnt):
            print(i+1,movie_type[i])
        tem = int(input('输入序号选择类型：').strip())
        if tem not in [1,2,3,4]:
            print('错误输入请重输。。。。\n')
        else:
            data = self.db[movie_type[tem-1]].find({},{'_id':0})
            for n,l in data[0].items():
                print("\nname: %s"%n)
                for j in l:
                    print('磁力链接：%s'%j.encode('gb2312','ignore'))

if __name__ == "__main__":
    url = 'https://www.dy2018.com'
    sp = Spdier(url)
    # sp.get_name()
    # print('爬取完成。。。。。')
    sp.show()