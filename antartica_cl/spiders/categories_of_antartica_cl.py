import scrapy
from urlparse import urlparse
from scrapy import Request
class CategoriesOfAntarticaCl(scrapy.Spider):

	name = "categories_of_antartica_cl"
	start_urls = ('https://www.antartica.cl/antartica/index.jsp',)

	use_selenium = False
	def parse(self, response):

		categories = response.xpath('//table[@width="116"]//a/@href').extract()

		for cate in categories:
			yield Request(response.urljoin(cate), callback=self.parse_categories)
			

	def parse_categories(sefl, response):

		categories = response.xpath('//table[@align="center"]//table[@cellspacing="0"]//table[@cellspacing="5"]//a/@href').extract()
		yield {'links':list(urlparse(x).path+'?'+x.split('?')[-1] for x in categories)}
