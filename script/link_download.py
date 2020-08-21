import os
import sys 
import logging
import urllib.request
import urllib.parse
from pic_info import PicInfo
import logging
import time
import sqlite3
from update_sql import update_sql
URL_HEADERS = { 
        'Content-Type': 'application/json;charset=utf-8'
}

max_queue_len = 100
def download_img(INIT_QUE,DOWNLOAD_QUE,lock):
    conn = sqlite3.connect("picinfo.db") 
    #cursor = conn.cursor()

    while True:
        cur_img = INIT_QUE.get()
        logging.info("INIT_QUE get size:%d" % INIT_QUE.qsize())
        if not cur_img:
            DOWNLOAD_QUE.put(None)
            logging.info("DOWNLOAD_QUE put size:%d None" % INIT_QUE.qsize())
            break
        if cur_img.status != PicInfo.INIT:
            logging.warn("img {} NOT INIT".format(cur_img.id))
            INIT_QUE.task_done()
            continue
        try:
            download_path = os.path.join("imgs",cur_img.country,cur_img.query,"%s.jpg" % cur_img.id)
            cover_request = urllib.request.Request(cur_img.url, method="GET", headers=URL_HEADERS)
            response = urllib.request.urlopen(cover_request)
            resp_header = response.info()
            content_type = resp_header["Content-Type"]
            image_type = content_type.split('/')
            if image_type[0] == "image" and len(image_type) == 2:
                type = image_type[1]
                #cover_file_name = '{}{}{}{}{}'.format(local_dir,os.sep, resid, ".", type)
                urllib.request.urlretrieve(cur_img.url, download_path)
                fsize = os.path.getsize(download_path)
                logging.debug("download "+ cur_img.url+"->"+download_path)
                if fsize < 100:
                    logging.warn("the file {} size is less than 100".format(cur_img.id))
                    logging.error("ERROR",cur_img.status)
                    cur_img.status = PicInfo.ERROR
                else:
                    cur_img.status = PicInfo.DOWNLOAD
                    if DOWNLOAD_QUE.qsize() > max_queue_len:
                        DOWNLOAD_QUE.join()
                    DOWNLOAD_QUE.put(cur_img)
                    logging.info("DOWNLOAD_QUE put size:%d" % DOWNLOAD_QUE.qsize())
        except Exception as e:
            logging.error(e)
            cur_img.status = PicInfo.ERROR
        update_sql(cur_img,conn,lock["sql"])
        INIT_QUE.task_done()

    #cursor.close()
    conn.close()

