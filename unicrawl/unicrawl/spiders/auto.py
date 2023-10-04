import json
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from colorama import Fore, Back, Style

class AutoSpider(CrawlSpider):
    name = "auto"
#    allowed_domains = ["bmtu.edu.vn", "tuyensinh.bmtu.edu.vn"]
    allowed_domains = ["huflit.edu.vn"]
    start_urls = ["https://huflit.edu.vn/"]
    rules = [
        Rule(LinkExtractor(allow=r"https://huflit\.edu\.vn/.*"), callback='parse_item', follow=True),
        #Rule(LinkExtractor(allow=r"https://tokyo-human\.edu\.vn/tin-tuc-chu-de/page/(4[0-9]|[5-8][0-9]|90)/.*"), follow=False),
    ]

    def __init__(self, *a, **kw):
        super(AutoSpider, self).__init__(*a, **kw)
        self.config_name = "DNT.json"
        self.config_path = "./spiders/configs"
        with open(f"{self.config_path}/{self.config_name}") as f:
            self.data = {**json.load(f)}
        print("Init")

    def parse_item(self, response):
        data = {
            "university": self.data['university'],
            "code": self.data["code"],
            "drop_from": self.data["drop_from"],
            "url": response.url,
        }
        for key in self.data['text'].keys():
            select_options = self.data['text'][key]
            for option in select_options:
                if option[1] == 'xpath':
                    data[key] = response.xpath(option[0]).getall()
                else:
                    data[key] = response.css(option[0]).getall()
                if len(data[key]) > 0:
                    break
        hasTitle = len(data['title']) > 0
        hasBody = len(data['body']) > 0
        if hasBody and hasTitle:
            self.log_info(f"Ok: {data['url']}, {len(data.keys())}")
        else:
            self.log_error(f"NOT: {data['url']}, {len(data.keys())}") 
        yield data

    def log_info(self, text):
        self.logger.info(text)
        print(Back.GREEN,text,Style.RESET_ALL)

    def log_error(self, text):
        self.logger.info(text)
        print(Back.RED,text,Style.RESET_ALL)
