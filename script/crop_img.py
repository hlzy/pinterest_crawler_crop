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
import cv2
from mtcnn.mtcnn import MTCNN
import math
from config import conf


IF_INIT  =  conf["IF_INIT"]
IF_CRAW  = conf["IF_CRAW"]
IF_DOWNLOAD  =conf["IF_DOWNLOAD"]
IF_CROP = conf["IF_CROP"]
IF_UPLOAD  =conf["IF_UPLOAD"]

max_queue_len = 100
min_confidece = 0.85
def check_face_info(img):
    """ 检查图中的人脸获取第一个"""
    detector = MTCNN()
    face_results = detector.detect_faces(img)
    if face_results is None:
        return None
    face_results.sort(key=lambda x: x["confidence"], reverse=True)
    h = img.shape[0]
    w = img.shape[1]
    for face_result in face_results:
        face_confid = face_result["confidence"]
        if face_confid < min_confidece:
            continue
        box = face_result["box"]
        width = box[2]
        height = box[3]
        face_size = width * height
        face_ratio = float(face_size) / float(w * h)
        return face_confid, face_ratio, box
    return None

def crop_img(DOWNLOAD_QUE,CROP_QUE,lock,face_ratio,process_number_dict):
    conn = sqlite3.connect("picinfo.db")
    while True:
        cur_img = DOWNLOAD_QUE.get()
        logging.info("DOWNLOAD_QUE get size:%d" % DOWNLOAD_QUE.qsize())
        #print(cur_img)
        if not cur_img:
            DOWNLOAD_QUE.put(None)
            if process_number_dict["crop"] > 1:
                process_number_dict["crop"] -= 1
            else:
                DOWNLOAD_QUE.put(None)
            break
        if cur_img.status != PicInfo.DOWNLOAD:
            logging.warn("img {} NOT DOWNLOAD".format(cur_img.id))
            DOWNLOAD_QUE.task_done()
            continue
        download_path = os.path.join("imgs",cur_img.country,cur_img.query,"%s.jpg" % cur_img.id)
        #print(download_path)
        if not os.path.exists(download_path):
            #print(download_path)
            logging.warn("img {} NOT Exists ".format(cur_img.id)+download_path)
            cur_img.status = PicInfo.ERROR
            update_sql(cur_img,conn,lock["sql"])
            DOWNLOAD_QUE.task_done()
            continue
        logging.info("img {} start crop".format(download_path))
        #ret = crop_face(cur_img)
        save_path = os.path.join("crop_imgs",cur_img.country,cur_img.query,str(cur_img.id))
        try:
            ret = crop_face(download_path,save_path)
            logging.info("img {} finish crop".format(download_path))
            if ret:
                cur_img.status = PicInfo.CROP
                if CROP_QUE.qsize() > max_queue_len:
                    CROP_QUE.join()
                logging.info("CROP_QUE put size:%d" % CROP_QUE.qsize())
                #若把裁减当作最后一步则在此位置就不放入CROP_QUE了
                if IF_UPLOAD:
                    CROP_QUE.put(cur_img)
            else:
                cur_img.status = PicInfo.ERROR
        except:
            cur_img.status = PicInfo.ERROR
        update_sql(cur_img,conn,lock["sql"])
        DOWNLOAD_QUE.task_done()
    conn.close()


def mkdirpath(path):
    buf = path.split("/")
    for i in range(len(buf)):
        if not  os.path.exists("/".join(buf[:i+1])):
            os.makedirs("/".join(buf[:i+1]))

def crop_face(download_path,save_path,face_rate=0.7):
    logging.info("img {} start crop xxxxxxxx".format(download_path))
    img = cv2.imread(download_path)
    face_box = check_face_info(img)
    if face_box is None:
        logging.warn("not found face! "+download_path)
        return False
    face_confid, face_ratio, box = face_box
    height,width = img.shape[:2]
    crop_height = crop_width = max(box[2],box[3])
    if crop_height < 50:
        logging.warn("face too small!")
        return
    img_ratio_height_width = height / width
    face_center_x = box[0] + box[2] / 2 
    face_center_y = box[1] + box[3] / 2 
    #print(height,width,box[2]/box[3])
    width_min_distance = min(face_center_x,width - face_center_x)
    height_min_distance = min(face_center_y,height - face_center_y)
    max_scale = min(2 * width_min_distance / crop_width, 2 * height_min_distance / crop_height)
    scale = min(math.sqrt(1 / face_rate),max_scale)
    #print(scale,math.sqrt(1 / face_rate),max_scale)
    logging.debug("set face centor[(%d, %d)" % (face_center_x, face_center_y))
    crop_height *= scale
    crop_width *= scale
    x = face_center_x - crop_width // 2
    y = face_center_y - crop_height // 2
    
    crop_path = os.path.join("%s_%s.jpg" % (save_path,str(face_rate)))
    mkdirpath(os.path.dirname(crop_path))
    logging.info("CROP_FINISH save to "+ str(crop_path))
    cv2.imwrite(crop_path,img[int(y): int(y+crop_height) ,int(x): int(x+crop_width)])
    return True

