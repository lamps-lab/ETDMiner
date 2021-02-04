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
    urls = [loc.string for loc in soup.find_all('loc')]
    return urls

if __name__ == '__main__':
    xml = 'https://escholarship.org/siteMapIndex.xml'
    """
    Only siteMapItem-00 to siteMapItem-19 have the contents we need among these sitemaps. That's why filtering them(from 7th item) on the next line
    """
    soup = make_soup(xml)
    sitemap_urls = get_xml_urls(soup)
    # Gets all the necessary sitemaps from the main sitemap
    itemSitemaps = sitemap_urls[7:] 
    # Loop through each sitemap
    for itemSitemapUrl in itemSitemaps:
        content_xml = itemSitemapUrl #"https://escholarship.org/siteMapItem-00.xml"    
        content_soup = make_soup(content_xml)
        content_urls = get_xml_urls(content_soup)
        #print(content_urls)
        
        """
        For each different sitemap-[Num] there will be seperate url[Num].txt
        """
        sitemapNum = content_xml[-6:-4] # Extracting the number from the item-sitemap url        
        urlfile_name = "url-"+ sitemapNum + ".txt"
        urlfile_path = "urls/"+urlfile_name
        
        with open(urlfile_path, "a") as urls_file:
            for url in content_urls:
                print(url)
                urls_file.write(url+ '\n')
