# -*- coding: utf-8 -*-
"""
Created on Sat Oct 01 15:09:44 2016

@author: Xiaoyu
"""

import re
import urllib2
import requests

def run_program(zipcode=0):
    import timeit
    starttime = timeit.default_timer()
    zipcode = str(zipcode)
    dig = digging('http://www.zillow.com/homes/for_sale/' + zipcode)
    dig.browseguide()
    for i in dig.houselink:
        dig.saveinfo(i)
    endtime = timeit.default_timer()
    print endtime - starttime

class digging():
    def __init__(self,url):
        self.url = url
        self.houselink = []
        self.propertyprice={}
        self.propertysize = {}
        self.subs = [self.url]
    
    def sublink(self,link):
        response = urllib2.urlopen(link)
        html = response.read()
        pattern = re.compile(r'>\d</a></li><li><a href="(.*?)" onclick="SearchMain\.changePage')
        rough = re.findall(pattern,html)

        for i in rough:
            if 'http://www.zillow.com'+i not in self.subs:
                self.subs.append('http://www.zillow.com'+i)

    
    def findhouse(self,page):
        response = urllib2.urlopen(page)
        html = response.read()
        pattern_url = re.compile(r'a href="/homedetails\b(.+?)zpid')
        search_url = re.findall(pattern_url, html)
        for i in search_url:
            if ('http://www.zillow.com/homedetails'+i+'zpid') not in self.houselink:
                self.houselink.append('http://www.zillow.com/homedetails'+i+'zpid')
    
    def browseguide(self):
        self.sublink(self.url)
        for i in self.subs:
            self.findhouse(i)
            self.sublink(i)


    
    def saveinfo(self,link):
        response = requests.get(link)
        response.encoding = 'ascii'
        html = response.text
        pattern_add = re.compile(r'data-address="(.*?)" class')
        add = re.findall(pattern_add, html)
        pattern_price = re.compile(r'For sale: \$(.*?)\.')
        price = re.findall(pattern_price,html)
        pattern_size = re.compile(r'sqft":"(.*?)",')
        size = re.findall(pattern_size,html)
        if add != [] and price !=[] and size != []:
            self.propertyprice[add[0]] = int(price[0].replace(',',''))
            self.propertysize[add[0]] = int(size[0].replace(',',''))
    

        


        
    
    
            