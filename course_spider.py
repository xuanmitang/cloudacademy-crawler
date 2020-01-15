import scrapy, json, requests, os, logging
from http.cookiejar import MozillaCookieJar
from scrapy.crawler import CrawlerProcess
import sys, argparse


class courseSpider(scrapy.Spider):
    name = 'courseSpider'

    def __init__(self, course_name=None, cookies=None, outdir=None, *args, **kwargs):
        super(courseSpider, self).__init__(*args, **kwargs)
        self.course_url = 'https://cloudacademy.com/course/%s' % course_name
        self.cookies = self.load_cookies(cookies)
        self.outdir = outdir

    def load_cookies(self, cookies_dir):
        cj = MozillaCookieJar()
        cj.load(cookies_dir)

        cookies = {}
        for cookie in cj:
            cookies[cookie.name] = cookie.value
        return cookies

    def start_requests(self):
        return [scrapy.Request(url=self.course_url,
                               cookies=self.cookies,
                               callback=self.parse_lesson)]

    def parse_lesson(self, response):
        isCompleted = "Course completed" in response.text
        pages = response.xpath("//a[@palette='lecture']")
        if(isCompleted):
            pages = response.xpath("//a[@palette='course']")

        for page in pages:
            relative_url = page.xpath(".//@href").extract_first()
            lesson_url = response.urljoin(relative_url)
            if not isCompleted or "results" != relative_url.split("/")[-2]:
                logging.info("begin to request lessons url.... " + lesson_url)

                yield scrapy.Request(url=lesson_url,
                                 cookies=self.cookies,
                                 callback=self.parse_video,
                                 dont_filter=True)

    def parse_video(self, response):
        lesson_name = self.get_lesson_name(response.request.url)

        video_url = self.get_video_url(response)

        subtitle_url = self.get_subtitle_url(response)

        self.download(subtitle_url, lesson_name, ".vtt")
        self.download(video_url, lesson_name, ".mp4")

    def get_video_url(self, response):
        video_sources_text = self.parse_response_text(response.text, '"sources"')
        video_sources = json.loads(video_sources_text)
        video_source_with_720p = list(
            filter(lambda source: source['quality'] == '720p' and source['type'] == 'video/mp4', video_sources))
        video_url = video_source_with_720p[0]['src']
        logging.info("success parse video url... " + video_url)
        return video_url

    def get_subtitle_url(self, response):
        subtitles_text = self.parse_response_text(response.text, '"subtitles"')
        subtitles = json.loads(subtitles_text)
        subtitle_with_en = list(filter(lambda subtitle: subtitle['lang'] == 'en', subtitles))
        subtitle_url = subtitle_with_en[0]['url']
        logging.info("success parse subtitle url... " + subtitle_url)
        return subtitle_url

    def parse_response_text(self, html_text, key_word):
        res = html_text
        begin1 = res.index(key_word + ':[')
        text = res[begin1:]
        return self.split(text, '[', ']')

    def get_lesson_name(self, request_url):
        uri_arr = request_url.split('/')
        folder_name = self.outdir + "/" + uri_arr[-3]
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        return folder_name + '/' + uri_arr[-2]

    def download(self, url, lesson_name, type):
        logging.info("begin download... " + url)
        videoResult = requests.get(url, stream=True, cookies=self.cookies)
        with open(lesson_name + type, 'wb') as f:
            for chunk in videoResult.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
        logging.info("success download... " + url)

    def split(self, str, beginStr, endStr):
        beginIndex = str.index(beginStr)
        endIndex = str.index(endStr) + 1

        return str[beginIndex:endIndex]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-course_name", help="course name")
    parser.add_argument("-cookies", help="the absolute directory of cookies.txt")
    parser.add_argument("-outdir", help="files download path")

    args = parser.parse_args()
    print(args)

    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })

    process.crawl(courseSpider, course_name=args.course_name, cookies=args.cookies, outdir=args.outdir)
    process.start()


if __name__ == "__main__":
    main()