from  multiprocessing import JoinableQueue,Process,Lock
import urllib
import requests
import time
import os
from pic_info import PicInfo
import sqlite3
from update_sql import insert_sql,update_sql
import logging

max_queue_len = 100
def get_link(word1,word2,max_num,id_m,INIT_QUE,lock,process_number_dict):
    conn = sqlite3.connect("picinfo.db") 
    #cursor = conn.cursor()
    keyword = "%s %s" % (word1,word2)
    country = word2
    headers={
        "accept":"application/json, text/javascript, */*, q=0.01"
        ,"accept-encoding":"gzip, deflate, br"
        ,"accept-language":"zh-CN,zh;q=0.9"
        ,"referer":"https://www.pinterest.com/"
        ,"sec-fetch-dest":"empty"
        ,"sec-fetch-mode":"cors"
        ,"sec-fetch-site":"same-origin"
        ,"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"
        ,"x-app-version":"4c60df9"
        ,"x-pinterest-appstate":"active"
        ,"x-requested-with":"XMLHttpRequest"
    }
    query = {
        "source_url": """/search/pins/?q={}&rs=typed""".format(keyword)
        ,"data": """{"options":{"isPrefetch":false,"query":"%s","scope":"pins"},"context":{}}""" % (keyword)
        ,"_": """{}""".format(int(time.time() * 1000))
    }
    query = "&".join(["%s=%s" % (k,urllib.request.quote(v,safe="")) for k,v in query.items()])
    root_url = "https://www.pinterest.com/resource/BaseSearchResource/get/?" 
    url = root_url + query
    logging.debug(url)
    ret = requests.get(url,headers=headers)
    info = ret.json()
    bookmark= info['resource']['options']['bookmarks'][0]
    img_result = 0
    for row in info['resource_response']['data']['results']:
        img_result += 1
        if img_result > max_num:
            break

        lock["id"].acquire()
        id = id_m[0]
        id += 1
        id_m[0] = id
        lock["id"].release()
        #url = row['images']['orig']['url']
        url = row['images']['474x']['url']
        cur_img = PicInfo(id=id,url=url,country=country,query=word1,status=PicInfo.INIT)
        insert_sql(cur_img,conn,lock["sql"])
        if INIT_QUE.qsize() > max_queue_len:
            INIT_QUE.join()
        INIT_QUE.put(cur_img)
    loop = 0
    while img_result < max_num and loop < 100:
        loop += 1
        query = {
            "source_url": """/search/pins/?q={}&rs=typed""".format(keyword)
            ,"data": """{"options":{"page_size":25,"query":"%s","scope":"pins","bookmarks":["%s"],"field_set_key":"unauth_react"},"context":{}}""" % (keyword, bookmark)
            ,"_": """{}""".format(int(time.time() * 1000))
            }
        query = "&".join(["%s=%s" % (k,urllib.request.quote(v,safe="")) for k,v in query.items()])
        url = root_url + query
        ret = requests.get(url,headers=headers)
        info = ret.json()
        bookmark= info['resource']['options']['bookmarks'][0]
        for row in info['resource_response']['data']['results']:
            img_result += 1
            if img_result > max_num:
                break
            lock["id"].acquire()
            id = id_m[0]
            id += 1
            id_m[0] = id
            lock["id"].release()
            url = row['images']['474x']['url']
            cur_img = PicInfo(id=id,url=url,country=country,query=word1,status=PicInfo.INIT)
            insert_sql(cur_img,conn,lock["sql"])
            if INIT_QUE.qsize() > max_queue_len:
                INIT_QUE.join()
            INIT_QUE.put(cur_img)
            logging.info("INIT_QUE put size:%d" % INIT_QUE.qsize())
            logging.debug("%s %s %s"% (img_result,max_num, url))

    if INIT_QUE.qsize() > max_queue_len:
        INIT_QUE.join()
#    INIT_QUE.put(None)
#    cursor.close()
    conn.close()
    #print("sub_pid",os.getpid())
    if process_number_dict["init"] > 1:
        process_number_dict["init"] -= 1
    else:
        INIT_QUE.put(None)
    print("sub_pid %d",os.getpid()," ",os.getppid())
    print("init job done",word1,word2)
