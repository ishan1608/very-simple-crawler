import pprint

from crawler.crawler import Crawler


class MyCrawler(Crawler):

    def done(self, result):
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(result)


space_crawler = MyCrawler('http://www.ishan1608.space')
space_crawler.VERBOSE = True
space_crawler.execute()
