# -*- coding: utf-8 -*-
import scrapy
from scrapy.exceptions import CloseSpider
from scrapy import Request
from urlparse import urlparse
from json import loads
from datetime import date
import re
import time
import datetime
class AntarticaClSpider(scrapy.Spider):

    name = "antartica_cl_spider"

    use_selenium = False
###########################################################

    def __init__(self, categories=None, *args, **kwargs):
        super(AntarticaClSpider, self).__init__(*args, **kwargs)

        if not categories:
            raise CloseSpider('Received no categories!')
        else:
            self.categories = categories
        self.start_urls = loads(self.categories).keys()

###########################################################

    def start_requests(self):
        for url in self.start_urls:
            yield Request(('https://www.antartica.cl')+url, callback=self.parse, meta={'CatURL':url})

###########################################################

    def parse(self, response):
        
        products = response.xpath('//table[@cellspacing="5"][1]//td[@valign="top" and @width="70"]/parent::tr[1]')

        print(len(products))
        if not products: return
        
        for i in products:
            item = {}

            item['Vendedor'] = 200
            item['ID'] = i.xpath('./td[2]/a/@href').extract_first().split('=')[-1]
            item['Title'] = i.xpath('./td[2]/a/text()').extract_first()
            item['Description'] = ' '.join(i.xpath('./td[2]/*[@class="txt"]//text()').extract()).replace('\r\n','').replace('\t','')

            price = ''.join(i.xpath('.//*[@class="precioResultadoC"]//text()').re(r'[\d.,]+'))
            
            if price:
                item['Price'] = price.replace('.','').replace(',','.')
                item['Currency'] = 'CLP'
            else:
                price = ''.join(i.xpath('.//*[@class="precioResultadoI"]//text()').re(r'[\d.,]+'))
                if price:
                    item['Price'] = price.replace(',','.').replace('.','')
                    item['Currency'] = 'CLP'
                else:
                    price = ''.join(i.xpath('.//*[@class="precioResultadoN"]//text()').re(r'[\d.,]+'))
                    if price:
                        item['Price'] = price.replace(',','.').replace('.','')
                        item['Currency'] = 'CLP'
                    else:
                        continue

            item['Category URL'] = response.meta['CatURL']
            item['Details URL'] = response.urljoin(i.xpath('./td[2]/a/@href').extract_first())
            item['Date'] = date.today()

            item['timestamp'] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
            item['image_url'] = response.urljoin(i.xpath('.//img/@src').extract_first())

            yield item
            
        next = response.xpath('//img[contains(@src, "btn_flecha_play_prendido")]/parent::a[1]/@href').extract()
        if next:
            yield Request(response.urljoin(next[0]), callback=self.parse, meta=response.meta)
        