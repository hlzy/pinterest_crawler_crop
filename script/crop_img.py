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

max_queue_len = 150
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

def crop_img(DOWNLOAD_QUE,CROP_QUE,lock,face_ratio=0.5):
    conn = sqlite3.connect("picinfo.db")
    while True:
        cur_img = DOWNLOAD_QUE.get()
        if not cur_img:
            CROP_QUE.put(None)
            break
        if cur_img.status != PicInfo.INIT:
            logging.warn("img {} NOT INIT".format(cur_img.id))
            DOWNLOAD_QUE.task_done()
            continue
        download_path = os.path.join("imgs",cur_img.country,cur_img.query,"%s.jpg" % cur_img.id)
        if not os.path.exists(download_path):
            logging.warn("img {} NOT Exists".format(cur_img.id))
            cur_img.status = PicInfo.ERROR
            update_sql(cur_img,conn,lock["sql"])
            DOWNLOAD_QUE.task_done()
            continue
        logging.info("img {} start crop".format(cur_img.id))
        ret = crop_face(download_path)
        logging.info("img {} finish crop".format(cur_img.id))
        if ret:
            cur_img.status = PicInfo.CROP
            if CROP_QUE.qsize() > max_queue_len:
                CROP_QUE.join()
            CROP_QUE.put(cur_img)
        else:
            cur_img.status = PicInfo.ERROR
        update_sql(cur_img,conn,lock["sql"])
        DOWNLOAD_QUE.task_done()
    conn.close()


def mkdirpath(path):
    buf = path.split("/")
    for i in range(len(buf)):
        if not  os.path.exists("/".join(buf[:i+1])):
            os.makedirs("/".join(buf[:i+1]))

def crop_face(download_path,face_rate=0.7):
    img = cv2.imread(download_path)
    face_box = check_face_info(img)
    if face_box is None:
        logging.warn("not found face!")
        return False
    face_confid, face_ratio, box = face_box
    height,width = img.shape[:2]
    crop_height = crop_width = max(box[2],box[3])
    img_ratio_height_width = height / width
    face_center_x = box[0] + box[3] / 2 
    face_center_y = box[1] + box[2] / 2 
    print(height,width,box[2]/box[3])
    width_min_distance = min(face_center_x,width - face_center_x)
    height_min_distance = min(face_center_y,height - face_center_y)
    max_scale = min(2 * width_min_distance / crop_width, 2 * height_min_distance / crop_height)
    scale = min(math.sqrt(1 / face_rate),max_scale)
    print(scale,math.sqrt(1 / face_rate),max_scale)
    logging.debug("set face centor[(%d, %d)" % (face_center_x, face_center_y))
    crop_height *= scale
    crop_width *= scale
    x = face_center_x - crop_width // 2
    y = face_center_y - crop_height // 2
    
    crop_path = os.path.join("crop_imgs","%s_%s.jpg" % ("2",str(face_rate)))
    mkdirpath(os.path.dirname(crop_path))
    cv2.imwrite(crop_path,img[int(y): int(y+crop_height) ,int(x): int(x+crop_width)])
    return True
