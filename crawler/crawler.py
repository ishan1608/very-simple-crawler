from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import urlopen

import lxml.html
import validators


class Crawler(object):
    MAX_URLS = 10
    MAX_DEPTH = 5
    VERBOSE = False

    def __init__(self, seed_url):
        """
        Crawler for the seed_url
        :param seed_url: URL to start crawling from
        """
        if not validators.url(seed_url):
            raise ValueError("URL provided isn't valid")
        self.seed_url = seed_url

        # Keeping track of pages visited
        self._url_count = 0
        self._parsed_urls = []

    def execute(self):
        """
        Call execute() to start crawling.
        When done calls `done(result)` with the result as dictionary
        :return: None
        """
        if self.VERBOSE:
            print('Crawling started. Seed URL: {}'.format(self.seed_url))
        url_store = self._crawl_url(self.seed_url, 1)
        self.done(url_store)

    def done(self, result):
        """
        Results are provided as an argument to this function.
        Caller should override this function.
        :param result: Result dictionary
        :return: None
        """
        raise NotImplementedError('You must provide an implementation for done()')

    def _crawl_url(self, page_url, depth):
        # Store traversed URLs
        self._parsed_urls.append(page_url)
        self._url_count += 1

        # Get page contents
        try:
            if self.VERBOSE:
                print('{} Crawling url: {}'.format(self._url_count, page_url))
            content = urlopen(page_url).read()
        except HTTPError as error:
            error_message = '{}: {}'.format(error.code, error.msg)
            if self.VERBOSE:
                print('{} Error accessing: {}\n{}'.format(self._url_count, page_url, error_message))
            return {
                'url': page_url,
                'file': None,
                'error': error_message
            }

        # Store html in a file
        file_name = 'html/page-{}.html'.format(self._url_count)
        file = open(file_name, 'wb')
        file.write(content)
        file.close()

        # Dictionary to contain this Page and it's children's information
        url_store = {
            'url': page_url,
            'file': file_name,
            'links': []
        }
        base_url = self._get_base_url(page_url)

        dom = lxml.html.fromstring(content)
        links = dom.xpath('//a/@href')
        for link in links:
            link_result = self._process_link(link, depth, base_url)
            if link_result is not None:
                url_store['links'].append(link_result)

        return url_store

    def _process_link(self, link, depth, base_url):
        # Clean up link by removing #<anything> and attaching base_url for relative urls
        link = link.split('#')[0]
        link = base_url + link if (link.startswith('/') or link == '') else link

        # Check if link has already been crawled
        if link in self._parsed_urls:
            return

        # Check if maximum depth has reached
        if depth >= self.MAX_DEPTH:
            return {
                'url': link,
                'status': 'Maximum depth({}) reached'.format(depth)
            }

        # Check if maximum urls have been crawled
        if self._url_count >= self.MAX_URLS:
            return {
                'url': link,
                'status': 'Maximum urls({}) crawled'.format(self._url_count)
            }

        # Crawl the link
        return self._crawl_url(link, depth + 1)

    @staticmethod
    def _get_base_url(url):
        """
        Utility function to extract base_url from the given url.
        Ex: Will extract `https://www.wired.com` from `https://www.wired.com/story/how-google-keeps-power-hungry-operations-carbon-neutral/`
        :param url: url
        :return: base_url
        """
        parsed_uri = urlparse(url)
        return '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
