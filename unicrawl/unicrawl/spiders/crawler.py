import scrapy
import json
from colorama import Fore, Back, Style
from urllib.parse import urljoin

class NavListCrawler(scrapy.Spider):
    """
    This spider crawls article links from each nav link
    """
    name = "list_crawler"
    user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'
#    start_urls = ["http://tbump.edu.vn/"]
    start_urls = ["http://www.tsqcb.edu.vn/tsqcb/cat/Dai-Hoc/"]

    def __init__(self):
        self.config_path = "/home/h4438/Desktop/app/unicrawl/unicrawl/spiders/configs"
        self.config_name = "ngo_quyen.json"
        self.log_list = []
        with open(f"{self.config_path}/{self.config_name}") as f:
            self.data = {**json.load(f)}
    
    def parse(self, response):
        navs = response.xpath(self.data['main_nav_xpath']).css("a")
        nav_links = [urljoin(response.url, n.attrib["href"]) for n in navs]
        self.log_info(f"Links: {len(nav_links)}, {nav_links[0]}")
        for link in nav_links:
            yield scrapy.Request(link, callback=self.parse_page)

    def parse_page(self, response):
        data = {
            "university": self.data['university'],
            "url": response.url,
        }
        for key in self.data.text.keys():
            key_name = key.replace("_xpath","")
            data[key_name] = response.xpath(self.data.text[key].get())
        
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