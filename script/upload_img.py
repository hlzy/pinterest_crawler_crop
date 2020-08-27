import sqlite3
import logging
import os
import time
from pic_info import PicInfo
import requests
import json
logging.basicConfig(level=logging.DEBUG)


class Nation(object):
    def __init__(self):
        self._n = dict()
        with open("script/nation.cfg","r") as f:
            for each in f.readlines():
                nation_short,nation_long = each.rstrip().split("\t")
                self._n[nation_long.lower()] = nation_short

    def __getitem__(self,l):
        return self._n.get(l,"None")

class CoverAdapter(object):
    """ 封面信息的 Adapter """
    def __init__(self):
        pass

    def upload_output_cover(self, file_cover): 
        API_UPLOAD_IMAGES = "http://ikxd-boss-test.yy.com/gameMeta/admin/file/regionUpload?region=999&isHash=true&dir=ikxd"
        if not os.path.exists(file_cover) or os.path.getsize(file_cover) < 100:
            return None
        image_files = {"file": open(file_cover, 'rb')}
        r = requests.post(API_UPLOAD_IMAGES, files=image_files, timeout=20)
        try:
            response = json.loads(r.text)
            if response.get("code") != 0:
                return None
            image_urls = response.get("data", {}).get("list", [])
            if len(image_urls) == 0:
                return None
            logging.info("upload image finished. result=%s", r.text)
            return image_urls[0]
        except Exception as e:
            logging.warn("read response failed. error=%s", e)
            return None



def get_imgs():
    conn = sqlite3.connect("picinfo.db") 
    cursor = conn.cursor()
    sql = """
    SELECT id,url,country,query FROM pic_info where status = {};
    """.format(PicInfo.CROP)
    cursor.execute(sql)
    imgs = []
    while True:
        ret = cursor.fetchone()
        if not ret:
            break;
        imgs.append(ret) 
    return imgs

#cover_id	string	N/A	N/A
#res_id	string	N/A	N/A
#res_type	string	N/A	N/A
#res_country	string	N/A	N/A
#ori_cover_url	string	N/A	N/A
#width	int	N/A	N/A
#height	int	N/A	N/A
#cover_url	string	N/A	N/A
#cover_info	string	N/A	N/A
#dt *	string	partition	N/A
#cover_id, res_id, res_country, width, height, cover_url

def main():
    imgs = get_imgs()
    adapter = CoverAdapter()
    n = Nation()
    with open("upload_file.txt","a+")  as f:
        for each in imgs:
            logging.debug(imgs[:2])
            id = str(each[0])
            url = each[1]
            country = each[2]
            query = each[3]
            imgs_path = os.path.join("crop_imgs",country,query,id) + "_0.7.jpg"
            if os.path.exists(imgs_path):
                logging.debug("exesits:" + imgs_path)
            else:
                logging.warn("exesits:" + imgs_path)
            upload_url = adapter.upload_output_cover(imgs_path)
            f.write("{cover_id}\t{res_id}\t{res_type}\t{res_country}\t{ori_cover_url}\t{width}\t{height}\t{cover_url}\t{cover_info}\n".format(
                cover_id=id
                ,res_id="0"
                ,res_type="0"
                ,res_country=n[country.lower()]
                ,ori_cover_url=url
                ,width = 100
                ,height = 100
                ,cover_url =  upload_url
                ,cover_info = "NULL"))

def test():
    n = Nation()
    print(n["china"])
    print(n["india"])
    print(n["xx"])
    #print(n.get("china"))
    #print(n.get("india"))

if __name__== "__main__":
    main()
