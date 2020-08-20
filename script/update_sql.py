import sqlite3
import logging

#        self.url= config.get("url")
#        self.id = config.get("id")
#        self.query = config.get("query","unkown")
#        self.country = config.get("country","unkown")
#        self.status = config.get("status",INIT)
#        self.width = config.get("width","-")
#        self.height = config.get("height","-")

def insert_sql(cur_img,conn,sql_lock):
    sql="""
    insert into pic_info(id,url,country,query,status) 
    values("{}","{}","{}","{}","{}")
    """.format(cur_img.id,
            cur_img.url,
            cur_img.country,
            cur_img.query,
            cur_img.status)
    sql_lock.acquire()
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    sql_lock.release()

def update_sql(cur_img,conn,sql_lock):
    sql="""
    update pic_info set 
    url = "{url}",
    country = "{country}",
    query = "{query}",
    status = {status},
    width = {width},
    height = {height}
    where id = {id}
    """.format(id=cur_img.id,
            url=cur_img.url,
            country=cur_img.country,
            status=cur_img.status,
            query=cur_img.query,
            width=cur_img.width,
            height=cur_img.height)
    sql_lock.acquire()
    cursor = conn.cursor()
    logging.debug(sql)
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    sql_lock.release()
