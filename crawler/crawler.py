import validators
from urllib.request import urlopen
from urllib.parse import urlparse
from urllib.error import HTTPError
import lxml.html


class Crawler(object):
    URL_PER_PAGE_LIMIT = 10

    def __init__(self, seed_url, depth=5):
        if not validators.url(seed_url):
            raise ValueError("URL provided isn't valid")
        self.seed_url = seed_url
        self.depth = depth

        # Keeping track of pages visited
        self._url_count = 0
        self._max_urls = self.URL_PER_PAGE_LIMIT * depth

        self._parsed_urls = []

    def execute(self):
        """
        Call execute() to start crawling
        :return:
        """
        url_store = self._crawl_url(self.seed_url, 1)
        self.done(url_store)

    def done(self, result):
        """
        Results are provided as an argument to this function.
        Caller should override this function.
        :param result: Result dictionary
        :return: None
        """
        raise NotImplementedError('')

    def _crawl_url(self, page_url, depth):
        self._parsed_urls.append(page_url)
        self._url_count += 1

        try:
            content = urlopen(page_url).read()
        except HTTPError as error:
            return {
                'url': page_url,
                'file': None,
                'error': '{}: {}'.format(error.code, error.msg)
            }

        file_name = 'html/page-{}.html'.format(self._url_count)
        file = open(file_name, 'wb')
        file.write(content)
        file.close()

        base_url = self.get_base_url(page_url)

        url_store = {
            'url': page_url,
            'file': file_name,
            'links': []
        }

        dom = lxml.html.fromstring(content)
        links = dom.xpath('//a/@href')
        for link in [link.split('#')[0] for link in links]:
            link_result = self._process_link(link, depth, base_url)
            if link_result is not None:
                url_store['links'].append(link_result)

        return url_store

    def _process_link(self, link, depth, base_url):
        link = base_url + link if (link.startswith('/') or link == '') else link
        if link in self._parsed_urls:
            return

        if depth >= self.depth:
            return

        if self._url_count > self._max_urls:
            return

        return self._crawl_url(link, depth + 1)

    @staticmethod
    def get_base_url(url):
        parsed_uri = urlparse(url)
        return '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
