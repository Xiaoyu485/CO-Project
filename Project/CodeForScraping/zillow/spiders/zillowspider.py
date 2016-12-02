import scrapy
import pickle

class ZillowSpider(scrapy.Spider):
    """A spider used to collect the normal housing information"""
    name = "zillows"
    # urls = ["http://www.zillow.com/homes/austin-tx-78731_rb/"]

    def start_requests(self):
        # urls = "http://www.zillow.com/homes/for_sale/78731_rb/"
        # yield scrapy.Request(url=urls, callback=self.parse)
        output = open('austinzip.txt', 'rb')
        zips = pickle.load(output)
        output.close()
        for zip in zips:
            url = "http://www.zillow.com/homes/for_sale/"+str(zip)+"_rb/"
            yield scrapy.Request(url=url, callback=self.parse)

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
                price = price.replace('+', '')
                floorarea = house.xpath('.//span[@class="zsg-photo-card-info"]/text()').re('([0-9,]*) sqft')[0]
                floorarea = floorarea.replace(',', '')
                bed = house.xpath('.//span[@class="zsg-photo-card-info"]/text()').extract()[0]
                bed = bed.split(' ')[0]
                bath = house.xpath('.//span[@class="zsg-photo-card-info"]/text()').re('([0-9.]*) ba')[0]
                bath = bath.split(' ')[0]

                yield {
                        'address': house.xpath('.//span[@itemprop="streetAddress"]/text()').extract_first(),
                        'city': house.xpath('.//span[@itemprop="addressLocality"]/text()').extract_first(),
                        'zipcode': house.xpath('.//span[@itemprop="postalCode"]/text()').extract_first(),
                        'latitude': house.xpath('.//meta').re('content="(.*)"')[0],
                        'longitude': house.xpath('.//meta').re('content="(.*)"')[1],
                        'price': price,
                        'bedrooms': bed,
                        'bathrooms': bath,
                        'floorarea': floorarea
                }
        next_page = response.css('.off ::attr(href)').extract_first()
        # # In case it is a relative url
        next_page = response.urljoin(next_page)
        yield scrapy.Request(next_page, callback=self.parse)

