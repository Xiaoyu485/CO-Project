# -*- coding: utf-8 -*-
"""
Created on Sat Oct 01 15:09:44 2016

@author: Xiaoyu
"""

import re
import urllib2


class digging():
    def __init__(self,url):
        self.url = url
        self.houselink = []
        self.propertyprice={}
    
    def sublink(self):
        response = urllib2.urlopen(self.url)
        html = response.read()
        pattern = re.compile(r'>\d</a></li><li><a href="(.*?)" onclick="SearchMain\.changePage')
        rough = re.findall(pattern,html)
        subs = [self.url]
        for i in rough:
            subs.append('http://www.zillow.com'+i)  
        return subs
    
    def findhouse(self,page):
        response = urllib2.urlopen(page)
        html = response.read()
        pattern_url = re.compile(r'homedetails\b(.+?)zpid')
        search_url = re.findall(pattern_url, html)
        for i in search_url:
            if ('http://www.zillow.com/homedetails'+i+'zpid') not in self.houselink:
                self.houselink.append('http://www.zillow.com/homedetails'+i+'zpid')
    
    def browseguide(self):
        subs = self.sublink()
        for i in subs:
            self.findhouse(i)
    
    def saveinfo(self,link):
        response = urllib2.urlopen(link)
        html = response.read()
        pattern_add = re.compile(r'data-address="(.*?)" class')
        add = re.findall(pattern_add, html)
        pattern_price = re.compile(r'For sale: (.*?)\.')
        price = re.findall(pattern_price,html)
        self.propertyprice[add[0]] = price[0]
    

        
if __name__ == '__main__':
    dig = digging('http://www.zillow.com/homes/for_sale/Austin-TX-78731/92642_rid/globalrelevanceex_sort/30.410707,-97.678071,30.284789,-97.862607_rect/12_zm/1_p/0_mmm/')
    sublink = dig.sublink()
    ##listening Send My Love
    dig.browseguide()
    for i in dig.houselink:
        dig.saveinfo(i)
        
    
    
            