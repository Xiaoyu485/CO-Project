import scrapy
import pickle

class ZillowSpider(scrapy.Spider):
    """A spider used to collect the nearby school informations"""
    name = "zillows1"
    # urls = ["http://www.zillow.com/homes/austin-tx-78731_rb/"]

    def start_requests(self):

        output = open('austinzip.txt', 'rb')
        zips = pickle.load(output)
        output.close()
        # url = "http://www.zillow.com/homes/for_sale/78731_rb/"
        # yield scrapy.Request(url=url, callback=self.parse)
        for zip in zips:
            url = "http://www.zillow.com/homes/for_sale/"+str(zip)+"_rb/"
            yield scrapy.Request(url=url, callback=self.parse)

    # Figure out how to do these queries using Selector Gadget, xpath
    def parse(self, response):
        for house in response.xpath('//article'):
            if len(house.xpath('.//span[@class="zsg-photo-card-info"]/text()').extract()) == 3:
                detail = house.xpath('.//div/a')[0].re('href="(.*)" ')[0]
                detail = response.urljoin(detail)
                yield scrapy.Request(detail, callback=self.detailparse)
        next_page = response.css('.off ::attr(href)').extract_first()
        # # In case it is a relative url
        next_page = response.urljoin(next_page)
        yield scrapy.Request(next_page, callback=self.parse)

    def detailparse(self, response):
        address = response.xpath('.//span[@itemprop="streetAddress"]/text()').extract_first()
        schooldistance = response.xpath('.//div[@class="nearby-schools-distance"]/text()').re('([0-9.].*) mi')
        schoolrating = response.css('.gs-rating-number ::text').extract()
        schoolrating = [int(i) for i in schoolrating]
        if schoolrating:
            bestschoolrating = max(schoolrating)
            index = schoolrating.index(bestschoolrating)
            bestschooldistnce = schooldistance[index]
            yield {
                    'schoolrating': bestschoolrating,
                    'schooldistance': bestschooldistnce,
                    'address': address}






