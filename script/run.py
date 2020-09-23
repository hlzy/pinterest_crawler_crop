#控制是否执行每个步骤
from  multiprocessing import JoinableQueue,Process,Lock,Manager,Pool
from pic_info import PicInfo
from link_craw import get_link
from link_download import download_img
from crop_img import crop_img
import os
import sqlite3
import time
import logging
from config import conf


IF_INIT  =  conf["IF_INIT"]
IF_CRAW  = conf["IF_CRAW"]
IF_DOWNLOAD  =conf["IF_DOWNLOAD"]
IF_CROP = conf["IF_CROP"]
IF_UPLOAD  =conf["IF_UPLOAD"]
IF_SKIP = conf["IF_SKIP"]


#设置日志级别
logging.basicConfig(level=logging.INFO)
main_word=["pretty face","preety woman"]
main_word=["normal girl face","normal girl face","beauty girl","beauty pictures","beauty woman","pretty girl","pretty woman","girl face","girl face"]
#main_word=["bikini"]
#countrys = "Indonesia Egypt Brazil Vietnam Thailand United States Pakistan Bangladesh Ukraine United Kingdom Russian Federation Kazakhstan Canada Malaysia Nepal Turkey Uzbekistan Germany Kyrgyzstan Armenia Jordan Belarus Algeria Morocco Netherlands France Yemen Georgia".split()
#countrys = "India,Indonesia,Vietnam,Thailand,Middle East,Brazil".split(",")
countrys = "india,pakistan".split(",")


max_number = 1000
#max_process_num = len(main_word) * len(countrys)
max_process_num = 4


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
        , height integer default 0
        , width integer default 0
        );
    """
    cursor.execute(sql)
    conn.commit()

    sql = """
    select id,url,country,query,status,height,width from pic_info where status <> {} and status <> {}
    """.format(PicInfo.UPLOAD,PicInfo.ERROR)
    cursor.execute(sql)
    while True:
        db_img_info = cursor.fetchone()
        if not db_img_info:
            break
        cur_img = PicInfo(id=db_img_info[0]
                ,url=db_img_info[1]
                ,country=db_img_info[2]
                ,query=db_img_info[3]
                ,status=db_img_info[4]
                ,height=db_img_info[5]
                ,width=db_img_info[6]
                )
        if cur_img.status == PicInfo.INIT and IF_SKIP:
            logging.info("INIT_QUE put size:%d" % INIT_QUE.qsize())
            INIT_QUE.put(cur_img)
        elif cur_img.status == PicInfo.DOWNLOAD and IF_SKIP:
            logging.info("DOWNLOAD_QUE put size:%d" % DOWNLOAD_QUE.qsize())
            DOWNLOAD_QUE.put(cur_img)
        elif cur_img.status == PicInfo.CROP and IF_SKIP:
            logging.info("CROP_QUE put size:%d" % CROP_QUE.qsize())
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
            logging.debug("relase %d"% index)
            a = each.get()
            if not a:
                break
            each.task_done()

def hello(word1,word2,max_num,id_m,INIT_QUE,lock): #,process_number_dict):
    print("hello")

def main():
    #conn = sqlite3.connect("picinfo.db",check_same_thread = False) 
    #爬取链接这一步若采用线程池则，队列使用Manager.Queue
    #爬去采用线程池主要是由于，查询关键词较多
    m = Manager()
    INIT_QUE = m.Queue()
    DOWNLOAD_QUE = JoinableQueue()
    CROP_QUE = JoinableQueue()
    UPLOAD_QUE = JoinableQueue()
    conn = sqlite3.connect("picinfo.db") 
    mkdirpath(os.path.join("imgs","unkown","unkown"))
    #cursor = conn.cursor()
    lock = {
        "sql": m.Lock()
        ,"id": m.Lock()
    }
    #1. 使用mysql初始化各队列之前未完成的任务
    if IF_INIT:
        init_que(INIT_QUE,DOWNLOAD_QUE,CROP_QUE,UPLOAD_QUE)
    start_id = get_id()
    manager = Manager()
    id_m = manager.list([start_id])
    #2. 爬取链接 
    get_link_task = []
    
    process_number_dict = m.dict()
    process_number_dict["init"] = len(main_word) * len(countrys)
    process_number_dict["download"] = max_process_num
    process_number_dict["crop"] = max_process_num
    pool = Pool(max_process_num)

    if IF_CRAW:
        for q1 in main_word:
            for q2 in countrys:
                mkdirpath(os.path.join("imgs",q2,q1))
                mkdirpath(os.path.join("crop_imgs",q2,q1))
                #pool.apply_async(hello,args=(q1,q2,max_number,id_m,INIT_QUE,lock,))#,process_number_dict,))
                pool.apply_async(get_link, args=(q1,q2,max_number,id_m,INIT_QUE,lock,process_number_dict,))
#                p = Process(target=get_link, args=(q1,q2,max_number,id_m,INIT_QUE,lock))
#                get_link_task.append(p)
    else:
        for _ in range(max_process_num):
            INIT_QUE.put(None)

    #3. 下载图片
    download_link_task = []
    if IF_DOWNLOAD:
        for _ in range(max_process_num):
            p = Process(target=download_img,args=(INIT_QUE,DOWNLOAD_QUE,lock,process_number_dict))
            #p.start()
            download_link_task.append(p)
    else:
        for _ in range(max_process_num):
            DOWNLOAD_QUE.put(None)

    
    #4. 裁减人脸
    print("*-"*10)
    crop_task = []
    if IF_CROP:
         for _ in range(max_process_num):
            p = Process(target=crop_img,args=(DOWNLOAD_QUE,CROP_QUE,lock,0.5,process_number_dict))
            #p.start()
            crop_task.append(p)
    else:
        for _ in range(max_process_num):
            CROP_QUE.put(None)

    print(len(get_link_task))
    print("main_pid",os.getpid()," ",os.getppid())
    for each in get_link_task + download_link_task + crop_task:
        print(each,"start")
        each.start()
    pool.close()
    pool.join()
    pool.terminate()
    for each in get_link_task + download_link_task + crop_task:
        each.join()
    print(DOWNLOAD_QUE.qsize())
    release_que([INIT_QUE,DOWNLOAD_QUE,CROP_QUE,UPLOAD_QUE])
    print("job done")

if __name__ == "__main__":
   main() 
