"""
    This program will go through the url-<Num>.txt files and -
    1. download pdf 
    2. extract metadata from html
"""
import urllib.request
import urllib.response
import urllib.parse
import bs4
import re
from collections import defaultdict
import json
import os
import time
from socket import timeout
import requests
import ssl
import time

base = "https://digitalcommons.odu.edu/cgi/"

# Bypassing SSL verification check
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Log stuffs
def print_logs(text):
    print(text)
    with open("log.txt",'a',encoding = 'utf-8') as f:
        f.write(text+"\n")

"""
    This module will help keep the op running just incase any URL error occurs
"""
def isPDFDownloadUrlWorkable(soup):
    
    downloadableUrl = getPDFdownloadUrl(soup)
    isWorkable = True
    # @Dennis add if, when downloadableUrl is None, return False
    if not downloadableUrl:
        isWorkable = False
        return isWorkable
    
    try:
        response = urllib.request.urlopen(downloadableUrl)
    except urllib.error.HTTPError as exception:
        print (exception)
        isWorkable = False
    except urllib.error.ContentTooShortError() as exception:
        print (exception)
        isWorkable = False
    except urllib.error.URLError as exception:
        print (exception)
        isWorkable = False
    except ConnectionResetError as exception:
        print (exception)
        isWorkable = False    
    
    return isWorkable

def getPDFdownloadUrl(soup):
    hrefValue = None
    anchortag = soup.find('div',class_='download-button')
    if anchortag:
        anchortag = anchortag.find('a',id='pdf')
        if anchortag:            
            hrefValue = anchortag['href'] 
    return hrefValue


def extractPDF(url,soup,ID):
    # Get the PDF download-able URL
    downloadableUrl = getPDFdownloadUrl(soup)
    print(downloadableUrl)
    # Extract item id    
    itemId = ID
    
    print(itemId)

    
    # Create directory based on item-id
    directory = 'etds/'+ itemId + '/'
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Download and store pdf to that directory
    fileName = itemId + '.pdf'
    filepath = os.path.join(directory, fileName)    
    #urllib.request.urlretrieve(downloadableUrl,filepath) # urllib.request.urlretrieve(source,dest)
    
    response = urllib.request.urlopen(downloadableUrl,context=ctx)
    with open(filepath, 'wb') as f:
        f.write(response.read())

    print("Successful pdf parsing for:"+itemId)

def saveHTML(url,response,soup,ID):
    # Extract item id
    #objId = soup.find('mets:mets')['objid']
    itemId = ID

    # Create directory based on item-id
    directory = 'etds/'+ itemId + '/'
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Define filename with item-id
    fileName = itemId + '.html'
    filepath = os.path.join(directory, fileName)  
    
    #print(response.decode('utf-8'))
    with open(filepath, 'wb') as file: # wb for override
        file.write(response)

def extractContents(url,ID):             
    isWorkable = True
    response = None
    try:
        response = urllib.request.urlopen(url)  # opens each link to be parsed
    except urllib.error.HTTPError as exception:
        print (exception)
        isWorkable = False
    except urllib.error.ContentTooShortError() as exception:
        print (exception)
        isWorkable = False
    except urllib.error.URLError as exception:
        print (exception)
        isWorkable = False
    except timeout: 
        print("==> Timeout")
        isWorkable = False
        
    if(isWorkable):
        print('Works!')
        response = response.read()
        soup = bs4.BeautifulSoup(response, "html.parser")
        
        #print(soup)
        #Check If item is thesis & PDF is download-able => then we'll do extraction
        print_logs("Now starting: "+ url)        
    
        if isPDFDownloadUrlWorkable(soup):                                
            extractPDF(url, soup,ID) # Completed            
        saveHTML(url,response,soup,ID) 
    else:
        print('Not good')


    time.sleep(2)  # variable delay, just maintain 10s overall


if __name__ == '__main__':
    #TODO: get url.txt lines and make handle url
    url_directory = 'urls/'       
    urlfile = 'urls.txt' 
    filepath = os.path.join(url_directory, urlfile) # Make relative path    
    text = open(filepath, 'r')
    data = text.readlines()        
    #print(len(data))
    for line in range(len(data)):        
        link = data[line].strip().split('\n') # remove '\n' from the url on each line    
        print(link)      
        
        item_Id = str(line) 
        directory = 'etds/'+ item_Id + '/'
        if not os.path.exists(directory):       
            extractContents(link[0],item_Id) # This will bring up landing page (if exists)
        else:
            print("pass", item_Id)    
