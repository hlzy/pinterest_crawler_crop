from  multiprocessing import JoinableQueue,Process,Lock
import urllib
import requests
import time
from pic_info import PicInfo
import sqlite3
from update_sql import insert_sql,update_sql

def get_link(word1,word2,max_num,id_m,INIT_QUE,lock):
    #conn = sqlite3.connect("picinfo.db") 
    #cursor = conn.cursor()
    #keyword = "%s %s" % (word1,word2)
    #country = word2
    #headers={
    #    "accept":"application/json, text/javascript, */*, q=0.01"
    #    ,"accept-encoding":"gzip, deflate, br"
    #    ,"accept-language":"zh-CN,zh;q=0.9"
    #    ,"referer":"https://www.pinterest.com/"
    #    ,"sec-fetch-dest":"empty"
    #    ,"sec-fetch-mode":"cors"
    #    ,"sec-fetch-site":"same-origin"
    #    ,"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"
    #    ,"x-app-version":"4c60df9"
    #    ,"x-pinterest-appstate":"active"
    #    ,"x-requested-with":"XMLHttpRequest"
    #}
    #query = {
    #    "source_url": """/search/pins/?q={}&rs=typed""".format(keyword)
    #    ,"data": """{"options":{"isPrefetch":false,"query":"beautiful girl","scope":"pins"},"context":{}}"""
    #    ,"_": """{}""".format(int(time.time() * 1000))
    #}
    #print(query)
    #query = "&".join(["%s=%s" % (k,urllib.request.quote(v,safe="")) for k,v in query.items()])
    #root_url = "https://www.pinterest.com/resource/BaseSearchResource/get/?" 
    #url = root_url + query
    #ret = requests.get(url,headers=headers)
    #info = ret.json()
    #bookmark= info['resource']['options']['bookmarks'][0]
    #img_result = 0
    #for row in info['resource_response']['data']['results']:
    #    lock["id"].acquire()
    #    id = id_m[0]
    #    id += 1
    #    id_m[0] = id
    #    lock["id"].release()
    #    url = row['images']['orig']['url']
    #    cur_img = PicInfo(id=id,url=url,country=country,query=word1,status=PicInfo.INIT)
    #    insert_sql(cur_img,conn,cursor,lock["sql"])
    #    INIT_QUE.put(cur_img)
    #loop = 0
    #while img_result < max_num and loop < 100:
    #    loop += 1
    #    query = {
    #        "source_url": """/search/pins/?q={}&rs=typed""".format(keyword)
    #        ,"data": """{"options":{"page_size":25,"query":"beautiful girl","scope":"pins","bookmarks":["%s"],"field_set_key":"unauth_react"},"context":{}}""" % bookmark
    #        ,"_": """{}""".format(int(time.time() * 1000))
    #        }
    #    query = "&".join(["%s=%s" % (k,urllib.request.quote(v,safe="")) for k,v in query.items()])
    #    url = root_url + query
    #    ret = requests.get(url,headers=headers)
    #    info = ret.json()
    #    bookmark= info['resource']['options']['bookmarks'][0]
    #    for row in info['resource_response']['data']['results']:
    #        img_result += 1
    #        lock["id"].acquire()
    #        id = id_m[0]
    #        id += 1
    #        id_m[0] = id
    #        lock["id"].release()
    #        url = row['images']['orig']['url']
    #        print(img_result, url)
    #        cur_img = PicInfo(id=id,url=url,country=country,query=word1,status=PicInfo.INIT)
    #        insert_sql(cur_img,conn,cursor,lock["sql"])
    #        INIT_QUE.put(cur_img)

    #INIT_QUE.put(None)
    #cursor.close()
    #conn.close()
    print("init job done",word1,word2)
