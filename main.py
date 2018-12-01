import json
from crawler.crawler import Crawler


class MyCrawler(Crawler):

    def done(self, result):
        print(json.dumps(result))


space_crawler = MyCrawler('http://www.ishan1608.space')
space_crawler.execute()
