# Very Simple Crawler
A very simple crawler to demonstrate storing of page's url, it's links and the page body as html.

## Build
`chmod +x linux_dependencies.sh`

`./linux_dependencies.sh`

`pip install -r requirements.txt`

## Run
In order to use the crawler, you need to extend the class `crawler.Crawler`, providing your implementation for `done()`.

Example:
    
    class MyCrawler(Crawler):

        def done(self, result):
            print(result)
    
    wired_crawler = MyCrawler('https://www.wired.com/')
    wired_crawler.execute()

An example is also provided in `example/main.py`
