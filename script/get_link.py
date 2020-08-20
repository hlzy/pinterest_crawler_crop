# encoding=utf8
import sys 

reload(sys)
sys.setdefaultencoding('utf8')
import urllib

import requests

headers={
    "accept": "application/json, text/javascript, */*, q=0.01",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en,zh-CN;q=0.9,zh;q=0.8",
    "referer": "https://www.pinterest.jp/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36",
    "x-app-version": "56ff0e7",
    "x-pinterest-appstate": "active",
    "x-requested-with": "XMLHttpRequest",
}

r = requests.get('https://www.pinterest.jp/resource/BaseSearchResource/get/?source_url=%2Fsearch%2Fpins%2F%3Fq%3D{preety}%2520girl%26rs%3Dtyped%26term_meta%5B%5D%3D{preety}%257Ctyped%26term_meta%5B%5D%3Dgirl%257Ctyped&data=%7B%22options%22%3A%7B%22isPrefetch%22%3Afalse%2C%22article%22%3Anull%2C%22appliedProductFilters%22%3A%22---%22%2C%22auto_correction_disabled%22%3Afalse%2C%22corpus%22%3Anull%2C%22customized_rerank_type%22%3Anull%2C%22filters%22%3Anull%2C%22query%22%3A%22{preety}%20girl%22%2C%22query_pin_sigs%22%3Anull%2C%22redux_normalize_feed%22%3Atrue%2C%22rs%22%3A%22typed%22%2C%22scope%22%3A%22pins%22%2C%22source_id%22%3Anull%7D%2C%22context%22%3A%7B%7D%7D&_=1597663114432'.format(preety='beauty'), headers=headers)
info = r.json()
# print json.dumps(r.json(), indent=4)
# exit()
cursor = info['resource']['options']['bookmarks'][0]
for i in range(2):
    query = { 
        "source_url": "/search/pins/?q=beauty%20girl&rs=typed&term_meta[]=beauty%7Ctyped&term_meta[]=girl%7Ctyped",
        'data': '{"options":{"page_size":25,"query":"beauty girl","scope":"pins","bookmarks":["%s"],"field_set_key":"unauth_react"},"context":{}}' % cursor,
        "_": "1597665356662",
    }   
    url = "https://www.pinterest.jp/resource/BaseSearchResource/get/?" + '&'.join(['%s=%s' % (k, urllib.quote(v)) for k, v in query.items()])
    r = requests.get(url, headers=headers)
    info = r.json()
    cursor = info['resource']['options']['bookmarks'][0]
    for row in info['resource_response']['data']['results']:
        #print row['grid_description']
        print row['images']['orig']['url']
