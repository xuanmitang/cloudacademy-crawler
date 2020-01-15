#1.install
```
pip3 install cloudacademy-crawler
```

#2.download cookies.txt file
```
1.Sign in to Cloud Academy, then use a browser extension to export cookies as cookies.txt.
(For Chrome, you can use the cookies.txt extension)

(The cookies.txt will expire in about two weeks, so you don't need to do this so frequently)
```

#3.run command in terminal
```
ca_spider -course_name=managing-findings-from-multiple-accounts-using-amazon-guardduty -cookies=/<cookie_dir>/cookies.txt -outdir=output
```
