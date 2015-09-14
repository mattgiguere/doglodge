import scrapy

class BfscrapSpider(scrapy.Spider):
    name = "bfscraps"
    allowed_domains = ["bringfido.com"]
    start_urls = [
        "http://www.bringfido.com/lodging/city/new_haven_ct_us/",
    ]

    def parse(self, response):
        filename = response.url.split("/")[-2] + '.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
