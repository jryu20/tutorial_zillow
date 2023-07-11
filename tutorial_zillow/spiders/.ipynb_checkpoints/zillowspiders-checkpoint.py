import scrapy 
from scrapy.http import Request
from selenium import webdriver
import scrapy
from bs4 import BeautifulSoup
import re
from scrapy.selector import Selector

 
class zillowspider(scrapy.Spider):

    name = "zillow"
        
    start_urls = ["https://www.realtor.com/realestateandhomes-search/Phoenix_AZ"]
        
    def parse(self, response):
        for house in response.css("div a::attr(href)").getall():    
            #for house in response.css("div > div.StyledPropertyCardDataWrapper-c11n-8-84-2__sc-1omp4c3-0.jIcpOJ.property-card-data > a::attr(href)").getall():
            yield response.follow(url=house,callback=self.parse_at_home)

        url = response.css("a.item.btn[aria-label='Go to next page']::attr(href)").getall()
        if url:
            next_page = "https://www.realtor.com" + url[-1]    
            yield response.follow(url=next_page,callback=self.parse)
            
    def parse_at_home(self,response):
        price = response.css("div.Price__Component-rui__x3geed-0.gipzbd::text").get()
            #info = response.css("div.layout-wrapper > div.layout-container > div.data-column-container > div.summary-container > div > div:nth-child(1) > div > div > div.hdp__sc-1s2b8ok-0.bhouud > div > div > span strong::text").getall()
        bed_bath_sqr = response.css("ul.PropertyMetastyles__StyledPropertyMeta-rui__sc-1g5rdjn-0.dAKbvN li span::text").getall()
        if price and bed_bath_sqr:
            yield {
                "price": price,
                "test": bed_bath_sqr
                }



