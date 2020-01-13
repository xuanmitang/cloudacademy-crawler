import scrapy
import json
import requests
import os


class videoSpider(scrapy.Spider):
    name = 'blogspider'
    # cj = MozillaCookieJar()
    # cj.load("cookies.txt")
    #
    # cookies = {}
    # for cookie in cj:
    #     cookies[cookie.name] = cookie.value
    # print(cookies)
    cookieObj = {'G_ENABLED_IDPS': 'google', '__adroll_fpc': 'e0050b80ca96a8a485f84a2925be0d1f-s2-1578646814262',
                 '__ar_v4': 'LNEP5K73PBCSXEQ7HVEWMH%3A20200109%3A2%7CADQBU3HLVZGJ5B4KCGOBWP%3A20200109%3A2%7CCI6SVWMBI5ACLLPFXALMKD%3A20200109%3A14%7CLR7R422TH5E73J4HSBXINB%3A20200109%3A14%7COOKBZUK2I5G6ZOXH2ETDWD%3A20200109%3A3%7CGGOYOLVGO5EIHC2JSAWDED%3A20200109%3A5%7CVB2KLGKSDBH5DAS6N7GG6U%3A20200112%3A1%7CNACBOQWG25CH7KGMRCCLQV%3A20200112%3A1',
                 '__hstc': '150207721.c5480994ed5cd6278288445c3fb24dfe.1578646824254.1578883431163.1578892961143.5',
                 '_delighted_fst': '1578883713687:{}', '_fbp': 'fb.1.1578646816568.379283505',
                 '_ga': 'GA1.2.463661897.1578646813', '_gaexp': 'GAX1.2.Ib2oyFHZRXCzqrrs9pv45w.18277.0',
                 '_gcl_au': '1.1.106495133.1578646812', '_gid': 'GA1.2.761523013.1578800018',
                 '_hjid': '04e088cf-ca5a-4d2c-b09c-338331e38b85', 'hubspotutk': 'c5480994ed5cd6278288445c3fb24dfe',
                 'optimizelyBuckets': '%7B%7D', 'optimizelyEndUserId': 'oeu1578646895173r0.4067294381527724',
                 'optimizelySegments': '%7B%22299877894%22%3A%22direct%22%2C%22299877895%22%3A%22gc%22%2C%22300068351%22%3A%22false%22%7D',
                 'DFTT_END_USER_PREV_BOOTSTRAPPED': 'true',
                 'ca_jwt': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Inh1YW5taXRhbmdAZ21haWwuY29tIiwib3JpZ19pYXQiOjE1Nzg4OTI5MTgsImZlYXR1cmVzIjpbXSwiY29ybl9jb21wYW55X2FjY291bnRfaWQiOm51bGwsImNvbXBhbnlfYWNjb3VudF9pZCI6bnVsbCwibWVtYmVyc2hpcF90aWVyIjoiaW5kaXZpZHVhbC15ZWFybHkiLCJ1c2VyX2lkIjoyNTcwNzcsImN1c3RvbWVyX2xpZmVjeWNsZSI6InRyaWFsLWFjdGl2ZSIsInRlbmFudF9pZCI6ImNsb3VkYWNhZGVteSIsImNvbXBhbnlfYWNjb3VudF9kb2VzX2NyZWF0ZV9wdWJsaWNfY29udGVudCI6bnVsbCwiYWN0b3JfaWQiOiI1ZTE4M2Q2ZjIyYzNmMjBiMjJjMGJlZmEiLCJleHAiOjE1Nzg4OTQxMTgsImVtYWlsIjoieHVhbm1pdGFuZ0BnbWFpbC5jb20ifQ.z2A-_7E3z_XRMbEsPxhevN0XbnY17d7HSlYfoO6vAU8',
                 'clouda-session': '4911d0eb-4d42-444f-8304-7493a8b31fa4',
                 'csrftoken': 'VBtDGxhi9Bp5qUvd7TWwj0e8vBW3NhofdIHaMYE6tbdbNYDx18gxjcDqMhULyVpY',
                 'driftt_aid': '40514fdf-d8b7-447f-afcb-c78751d4afb2', 'sessionid': '800w8lcx17tbwve4w0oshq4qf646epzu'}
    start_url = "https://cloudacademy.com/course/introduction-to-azure-container-service-acs/introduction-to-azure-container-service/"

    def start_requests(self):
        return [scrapy.Request(url=self.start_url,
                               cookies=self.cookieObj,
                               callback=self.parse_lesson_url)]

    def parse_lesson_url(self, response):
        pages = response.xpath("//a[@palette='lecture']")
        for page in pages:
            relative_url = page.xpath(".//@href").extract_first()
            lesson_url = response.urljoin(relative_url)

            print("begin to request lessons url....", lesson_url)

            yield scrapy.Request(url=lesson_url,
                                 cookies=self.cookieObj,
                                 callback=self.parse_video_url,
                                 dont_filter=True)

    def parse_video_url(self, response):
        # get video url from response
        res = response.text
        begin1 = res.index('"sources":[')
        text = res[begin1:]
        text2 = self.split(text, '[', ']')
        sources = json.loads(text2)
        result = filter(lambda source: source['quality'] == '720p' and source['type'] == 'video/mp4', sources)
        srcList = list(result)
        src = srcList[0]['src']

        print("success parse video url...", src)

        # get file name
        request_url = response.request.url.split('/')
        folder_name = request_url[-3]
        file_name = folder_name + '/' + request_url[-2] + '.mp4'

        print("begin download video...", file_name)

        videoResult = requests.get(src, stream=True, cookies=self.cookieObj)

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        with open(file_name, 'wb') as f:
            for chunk in videoResult.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
        print("success")

    def split(self, str, beginStr, endStr):
        beginIndex = str.index(beginStr)
        endIndex = str.index(endStr) + 1

        return str[beginIndex:endIndex]
