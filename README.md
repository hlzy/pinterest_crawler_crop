填写要爬取的主、副关键词后运行
"""
python3 script/run.py
"""

图片去重可以参考
"""
find imgs -name "*.jpg" |xargs -i@ md5sum @|sort |awk '{if(a[$1]++ ==0) print }' >tmp
cat tmp|cut -c 35-|head
"""
