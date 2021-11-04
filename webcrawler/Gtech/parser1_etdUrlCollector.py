"""
    GTech robots: https://smartech.gatech.edu/robots.txt
    Main Sitemaps: https://smartech.gatech.edu/sitemap
    Main has two different sitemap locations.

    Crawl delay: 10 
    This parser will go to each link and extract the links from those sitemaps and create a set of text files with the urls.    
"""
import requests
from bs4 import BeautifulSoup
from io import StringIO
import os
import time

def make_soup(url):
    r = requests.get(url, verify=False)
    soup = BeautifulSoup(r.text, 'lxml')
    return soup

def get_xml_urls(soup):
    urls = [loc.string for loc in soup.find_all('loc')]
    return urls

if __name__ == '__main__':    
    """
        map=0 => 50000 
            url-00 - url-01 - url-02 - url-03 - url-04 => 10000 each
        map=1 => 9145
            url-1
    """
    xml = 'https://smartech.gatech.edu/sitemap?map=0'
    soup = make_soup(xml)
    urls = get_xml_urls(soup)    
    with open("urls/urls-00.txt", "a") as urls_file:
        for url in urls[0:10000]:
            print(url)
            urls_file.write(url+ '\n')    
    
    #print(len(urls[40000:50000]))
