
import scrapy
import pickle

class ZillowSpider(scrapy.Spider):
    name = "zillows2"
    # urls = ["http://www.zillow.com/homes/austin-tx-78731_rb/"]

    def start_requests(self):
        urls = "http://www.zillow.com/homes/for_sale/78731_rb/"
        yield scrapy.Request(url=urls, callback=self.parse)
        # output = open('austinzip.txt', 'rb')
        # zips = pickle.load(output)
        # output.close()
        # for zip in zips:
        #     url = "http://www.zillow.com/homes/for_sale/"+str(zip)+"_rb/"
        #     yield scrapy.Request(url=url, callback=self.parse)

    # Figure out how to do these queries using Selector Gadget, xpath
    def parse(self, response):
        for house in response.xpath('//article'):
            if len(house.xpath('.//span[@class="zsg-photo-card-info"]/text()').extract()) == 3 and \
                    house.xpath('.//span[@class="zsg-photo-card-price"]/text()').extract_first():
                # detail = house.xpath('.//div/a')[0].re('href="(.*)" ')[0]
                # detail = response.urljoin(detail)
                # yield scrapy.Request(detail, callback=self.detailparse)
                price = house.xpath('.//span[@class="zsg-photo-card-price"]/text()').re('([0-9,].*)')[0]
                price = price.replace(',', '')
                floorarea = house.xpath('.//span[@class="zsg-photo-card-info"]/text()').re('([0-9,]*) sqft')[0]
                floorarea = floorarea.replace(',', '')

                yield {
                        'address': house.xpath('.//span[@itemprop="streetAddress"]/text()').extract_first(),
                        'city': house.xpath('.//span[@itemprop="addressLocality"]/text()').extract_first(),
                        'zipcode': house.xpath('.//span[@itemprop="postalCode"]/text()').extract_first(),
                        'latitude': house.xpath('.//meta').re('content="(.*)"')[0],
                        'longitude': house.xpath('.//meta').re('content="(.*)"')[1],
                        'price': house.xpath('.//span[@class="zsg-photo-card-price"]/text()').extract_first(),
                        'bedrooms': house.xpath('.//span[@class="zsg-photo-card-info"]/text()').extract()[0],
                        'bathrooms': house.xpath('.//span[@class="zsg-photo-card-info"]/text()').extract()[1],
                        'floorarea': house.xpath('.//span[@class="zsg-photo-card-info"]/text()').extract()[2]
                }
        next_page = response.css('.off ::attr(href)').extract_first()
        # # In case it is a relative url
        next_page = response.urljoin(next_page)
        yield scrapy.Request(next_page, callback=self.parse)

    # def detailparse(self, response):
    #     schoolrating = response.css('.gs-rating-number ::text').extract()
    #     schoolgrades = response.css('.clearfix .nearby-schools-grades ::text').extract()
    #     school_len = len(schoolgrades)
    #     item = {}
    #
    #     if school_len == 1:
    #         yield {
    #             'school1grades': schoolgrades[0],
    #             'school1rating': schoolrating[0],
    #         }
    #     elif school_len == 2:
    #         yield {
    #             'school1grades': schoolgrades[0],
    #             'school1rating': schoolrating[0],
    #             'school2grades': schoolgrades[1],
    #             'school2rating': schoolrating[1],
    #         }
    #     elif school_len == 3:
    #         yield {
    #             'school1grades': schoolgrades[0],
    #             'school1rating': schoolrating[0],
    #             'school2grades': schoolgrades[1],
    #             'school2rating': schoolrating[1],
    #             'school3grades': schoolgrades[2],
    #             'school3rating': schoolrating[2],
    #         }

