from  multiprocessing import JoinableQueue,Process,Lock,Manager
from pic_info import PicInfo
from link_craw import get_link
from link_download import download_img
import os
import sqlite3
import time
import logging

main_word=["pretty face","lovely girl"]
countrys = ["india","japan"]

main_word=["pretty face"]
countrys = ["india"]


max_number = 20
max_process_num = 1


def get_id():
    conn = sqlite3.connect("picinfo.db") 
    cursor = conn.cursor()
    sql = """
    SELECT max(id) FROM pic_info;
    """
    cursor.execute(sql)
    ret = cursor.fetchone()[0]
    id = 0
    if ret != None:
        id = int(ret)
    return id


def init_que(INIT_QUE,DOWNLOAD_QUE,CROP_QUE,UPLOAD_QUE):
    conn = sqlite3.connect("picinfo.db") 
    cursor = conn.cursor()
    sql = """
    CREATE TABLE IF NOT EXISTS pic_info (
        id integer primary key
        , url varchar(100)
        , country varchar(10)
        , query varchar(10)
        , status integer
        , height integer
        , width integer
        );
    """
    cursor.execute(sql)
    conn.commit()

    sql = """
    select id,url,status from pic_info where status <> {} and status <> {}
    """.format(PicInfo.UPLOAD,PicInfo.ERROR)
    cursor.execute(sql)
    while True:
        db_img_info = cursor.fetchone()
        if not db_img_info:
            break
        cur_img = PicInfo(id=db_img_info[0],url=db_img_info[1],status=db_img_info[2])
        if cur_img.status == PicInfo.INIT:
            INIT_QUE.put(cur_img)
        elif cur_img.status == PicInfo.DOWNLOAD:
            DOWNLOAD_QUE.put(cur_img)
        elif cur_img.status == PicInfo.CROP:
            CROP_QUE.put(cur_img)

    #这个sleep比较牛逼,防止垃圾回收时还有在执行put的queue 引发Broken pipe
    #1.put操作本色是异步的
    #time.sleep(5) 
    #由于sleep时间根据入库量大小决定不好控制更改到release_que单独去释放算了
    cursor.close()
    conn.close()


def mkdirpath(path):
    buf = path.split("/")
    for i in range(len(buf)):
        if not  os.path.exists("/".join(buf[:i+1])):
            os.makedirs("/".join(buf[:i+1]))

def release_que(queue_list):
    index = 0
    for each in queue_list:
        while not each.empty():
            index += 1
            logging.debug("relase",index)
            a = each.get()
            if not a:
                break
            each.task_done()
     

def main():
    #conn = sqlite3.connect("picinfo.db",check_same_thread = False) 
    INIT_QUE = JoinableQueue()
    DOWNLOAD_QUE = JoinableQueue()
    CROP_QUE = JoinableQueue()
    UPLOAD_QUE = JoinableQueue()
    conn = sqlite3.connect("picinfo.db") 
    mkdirpath(os.path.join("imgs","unkown","unkown"))
    #cursor = conn.cursor()
    lock = {
        "sql": Lock()
        ,"id": Lock()
    }
    #1. 使用mysql初始化各队列之前未完成的任务
    init_que(INIT_QUE,DOWNLOAD_QUE,CROP_QUE,UPLOAD_QUE)
    start_id = get_id()
    manager = Manager()
    id_m = manager.list([start_id])
    #2. 爬取链接 
    get_link_task = []
    for q1 in main_word:
        for q2 in countrys:
            mkdirpath(os.path.join("imgs",q2,q1))
            p = Process(target=get_link, args=(q1,q2,max_number,id_m,INIT_QUE,lock))
            get_link_task.append(p)
    #3. 下载图片
    download_link_task = []
    for _ in range(max_process_num):
        p = Process(target=download_img,args=(INIT_QUE,DOWNLOAD_QUE,lock))
        #p.start()
        download_link_task.append(p)
    print("*-"*10)
    print(len(get_link_task))
    print("main_pid",os.getpid()," ",os.getppid())
    for each in get_link_task + download_link_task:
        print(each,"start")
        each.start()
    for each in get_link_task + download_link_task:
        each.join()
#    print("???????????????????????????????????????"*5)
    print(DOWNLOAD_QUE.qsize())
    release_que([INIT_QUE,DOWNLOAD_QUE,CROP_QUE,UPLOAD_QUE])
    print("job done")

if __name__ == "__main__":
   main() 
