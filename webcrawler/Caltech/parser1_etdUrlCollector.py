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
    soup = BeautifulSoup(r.text, 'lxml')     
    return soup

def get_xml_urls(soup):
    urls = [eprintLocation['rdf:resource'] for eprintLocation in soup.find_all('ep:haseprint')]
    return urls

if __name__ == '__main__':
    xml = 'https://thesis.library.caltech.edu/cgi/export/repository/RDFXML/caltechthesis.rdf'

    soup = make_soup(xml)
    etdLocations = get_xml_urls(soup)        
    print(len(etdLocations))    
    # @Dennis
    # with open("urls/urls01.txt", "w") as urls_file:
    #     for url in etdLocations[5001:]: # 00 => 0-5000 ; 01 => 5001-rest
    #         print(url)
    #         urls_file.write(url+ '\n')  
    

    with open("urls/urls.txt", "w") as urls_file:
        for url in etdLocations: 
            print(url)
            urls_file.write(url+ '\n')  