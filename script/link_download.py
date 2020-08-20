import os
import sys 
import logging
import urllib.request
import urllib.parse
from pic_info import PicInfo
import logging
import time
import sqlite3
URL_HEADERS = { 
        'Content-Type': 'application/json;charset=utf-8'
}

def download_img(INIT_QUE,DOWNLOAD_QUE,lock):
    conn = sqlite3.connect("picinfo.db") 
    cursor = conn.cursor()

    while True:
        cur_img = INIT_QUE.get()
        if not cur_img:
            break
        if cur_img.status != PicInfo.INIT:
            logging.warn("img {} NOT INIT".format(cur_img.id))
            INIT_QUE.task_done()
            continue
        try:
            download_path = os.path.join("imgs",cur_img.countrys,cur_img.query,"%s.jpg" % cur_img.id)
            cover_request = urllib.request.Request(cur_img.url, method="GET", headers=URL_HEADERS)
            response = urllib.request.urlopen(cover_request)
            resp_header = response.info()
            content_type = resp_header["Content-Type"]
            image_type = content_type.split('/')
            if image_type[0] == "image" and len(image_type) == 2:
                type = image_type[1]
                #cover_file_name = '{}{}{}{}{}'.format(local_dir,os.sep, resid, ".", type)
                urllib.request.urlretrieve(url_path, download_path)
                fsize = os.path.getsize(cover_file_name)
                if fsize < 100:
                    logging.warn("the file {} size is less than 100".format(cur_img.id))
                    cur_img.status = PicInfo.ERROR
                else:
                    cur_img.starts = PicInfo.DOWNLOAD
                    DOWNLOAD_QUE.put(cur_img)
        except:
            cur_img.status = PicInfo.ERROR
        INIT_QUE.task_done()
        update_sql(cur_img,conn,cursor,lock["sql"])

    cursor.close()
    conn.close()

