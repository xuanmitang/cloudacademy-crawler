（目前只支持下载代码，本地运行）
#install
```
pip install scrapy
```

#download cookies.txt file
```
1.Sign in to Cloud Academy, then use a browser extension to export cookies as cookies.txt.

2.Put cookies.txt in source code directory. 
(The cookies.txt will expire in about two weeks, so you don't need to do this so frequently).

3.For Chrome, you can use the cookies.txt extension.
```

#update course_url
```
update course_url in aws_course_spider.py
```

#run
```
in terminal run command:
scrapy runspider aws_course_spider.py
```