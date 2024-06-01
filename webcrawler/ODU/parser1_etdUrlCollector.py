"""
    UC System has one main sitemap file which has 20 different sitemap locations.
    This parser will go to each link and extract the links from those sitemaps and create a set of text files with the urls.

    TESTED and works!
"""
import requests
from bs4 import BeautifulSoup
from io import StringIO
import os

def make_soup(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'xml')     
    return soup

def get_xml_urls(soup):    
    sitempaps = soup.find_all('sitemap')
    urls = []
    for sitemap in sitempaps:
        if 'etds' in sitemap.find('loc').text:
            urls.append(sitemap.find('loc').text)    
    return urls

def get_final_urls(etdLocations):
    final_etds = []
    for url in etdLocations:
        soup = make_soup(url)
        locs = soup.find_all('loc')
      
        for loc in locs:
            
            if loc.text[-2].isdigit():
                final_etds.append(loc.text)
    return final_etds

if __name__ == '__main__':
    xml = 'https://digitalcommons.odu.edu/siteindex.xml'

    soup = make_soup(xml)
    etdLocations = get_xml_urls(soup)   
    final_etds = get_final_urls(etdLocations) 
        
    # print(len(final_etds))    
    

    with open("urls/urls_index.txt", "w") as urls_file:
        for url in etdLocations: 
            print(url)
            urls_file.write(url+ '\n')  
            
    with open("urls/urls.txt", "w") as urls_file:
        for url in final_etds: 
            print(url)
            urls_file.write(url+ '\n') 