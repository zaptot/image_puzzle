from lxml import html
import os
import requests
import urllib.parse
import re
import cv2
import progressbar
from urllib.parse import urlparse
from threading import Thread


class DownloadThread(Thread):

    def __init__(self, urls, crawler, name, progressbar):
        """Инициализация потока"""
        Thread.__init__(self)
        self.daemon = True
        self.urls = urls
        self.crawler = crawler
        self.name = name
        self.bar = progressbar

    @staticmethod
    def uri_validator(x):
        try:
            result = urlparse(x)
            return all([result.scheme, result.netloc, result.path])
        except:
            return False

    def run(self):
        """Запуск потока"""
        for url in self.urls:
            if not DownloadThread.uri_validator(url):
                continue
            try:
                content = requests.get(urllib.parse.unquote(url), timeout=5).content
            except:
                continue
            self.crawler.save_image(url, content)
            self.bar.update(self.bar.value + 1)

class Crawler:

    COUNT_OF_IMAGES = 1000

    def __init__(self, folder="imgs"):
        self.folder = folder

    def get_urls_from_jsons(self, jsons):
        res = []
        for i in jsons:
            url = re.search(r'"ou":"([^"]*)', str(i)).group(1)
            res.append(url)
        return res

    def get_images(self, words, folder=0, count=COUNT_OF_IMAGES):
        folder = folder or self.folder
        current_count = 0
        if not os.path.exists(folder):
            os.makedirs(folder)
        print("Downloading images")
        with progressbar.ProgressBar(max_value=count, redirect_stdout=True) as bar:
            for word in words:
                page_number = 0
                word = urllib.parse.quote(word)
                while current_count < count:
                    url = f"https://www.google.com/search?hl=be&yv=3&q={word}&tbm=isch&ijn={page_number}&start={page_number * 100}&asearch=ichunk&async=_id:rg_s,_pms:s,_fmt:pc"
                    page = requests.get(url, headers=Crawler.headers())
                    doc = html.fromstring(re.search(r'<.*>', str(page.content))[0])
                    urls = doc.xpath('//div[@class = "rg_meta notranslate"]/text()')
                    urls = self.get_urls_from_jsons(urls)
                    if len(urls) < 1:
                         print("No more images!!")
                         break
                    threads = []
                    for i in range(0, 100, 10):
                        thread = DownloadThread(urls[i:i + 10], self, str(i/10), bar)
                        thread.start()
                        threads.append(thread)

                    for i in range(len(threads)):
                        threads[i].join()

                    current_count += 100
                    bar.update(current_count % count)

                    page_number += 1

    def save_image(self, url, content):
        with open(self.folder + '/' + str(hash(url)) + ".jpg", 'wb') as f:
            f.write(content)

    @staticmethod
    def headers():
        return {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
        }

def main():
    c = Crawler()
    c.get_images(["шварц", "драконы"])

if __name__ == "__main__":
    main()