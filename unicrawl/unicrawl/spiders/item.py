from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class EDU(CrawlSpider):
	name = 'edu'
	start_urls = ['http://tdnu.edu.vn']
	allowed_domains = ['tdnu.edu.vn']
	rules = [
		Rule(LinkExtractor(allow=['']), follow=True, callback='parse')
	]

	def parse(self, response):
		if response.css('title') is None:
			return
		
		title = response.css('title::text').extract_first()
		content = '\n'.join(
			response.css('main#main').getall()
		)

		if content is not None:
			yield {
				'title': title,
				'url': response.url,
				'content': content
			}
