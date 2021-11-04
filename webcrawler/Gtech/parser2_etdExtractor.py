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

base = "https://smartech.gatech.edu/"

# Bypassing SSL verification check
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Log stuffs
def print_logs(text):
    print(text)
    with open("log.txt",'w',encoding = 'utf-8') as f:
        f.write(text+"\n")

"""
    This module will help keep the op running just incase any URL error occurs
"""
def isPDFDownloadUrlWorkable(soup):
    downloadableUrl = getPDFdownloadUrl(soup)
    
    isWorkable = True
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

def ifPDFAllowed(soup):
    allowed = False
    hrefValue = ""
    # If PDF avalilable
    if soup.find('mets:file',mimetype="application/pdf"):
        hrefValue = soup.find('mets:file',mimetype="application/pdf").find('mets:flocat')['xlink:href']
    yFound =  re.search(r"(isAllowed=y)+", hrefValue)    
    
    if yFound is not None:
        allowed = True
    
    return allowed

def getPDFdownloadUrl(soup):
    hrefValue = soup.find('mets:file',mimetype="application/pdf").find('mets:flocat')['xlink:href']
    downloadableUrl = urllib.parse.urljoin(base, hrefValue)
    return downloadableUrl

# Check if it is a thesis [from breadcrumb]
def isItemThesis(soup):
    isThesis = False
    contentType = soup.find('dim:field', element="type")    
    if contentType is None:
        return False # If contentType not exists, return false already!
    
    contentTypeText = contentType.get_text()
    if re.match("(Dissertation)+", contentTypeText) or re.match("(Thesis)+", contentTypeText) or re.match("(Theses and Dissertations)+", contentTypeText):
        isThesis = True

    return isThesis

def extractPDF(url,soup):
    # Get the PDF download-able URL
    downloadableUrl = getPDFdownloadUrl(soup)
    print(downloadableUrl)
    # Extract item id
    objId = soup.find('mets:mets')['objid']
    itemId = objId.split("/")[-1]
    
    print(itemId)

    """
        TODO: Download and store the PDF. [Make sure folder with ID exists]        
        etds -> <itemID[D]> -> itemID.pdf | itemID.json
    """
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

def saveXML(response,soup):
    # Extract item id
    objId = soup.find('mets:mets')['objid']
    itemId = objId.split("/")[-1]

    # Create directory based on item-id
    directory = 'etds/'+ itemId + '/'
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Define filename with item-id
    fileName = itemId + '.xml'
    filepath = os.path.join(directory, fileName)  
    
    #print(response.decode('utf-8'))
    with open(filepath, 'wb') as file: # wb for override
        file.write(response)

def extractContents(url):     
    print(url) 
       
    #response = urllib.request.urlopen(url, context=ctx)  # opens each link to be parsed
    
    isWorkable = True
    response = None
    try:
        response = urllib.request.urlopen(url, context=ctx)  # opens each link to be parsed
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
        response = response.read()
        soup = bs4.BeautifulSoup(response, "lxml")
        print('Works!')
        #print(soup)
        # Check If item is thesis & PDF is download-able => then we'll do extraction
        print_logs("Now starting: "+ url)
        #ifPDFAllowed(soup)
        if isItemThesis(soup):
            print_logs("It's thesis")            
            #If PDF not allowed of available, just take the XML
            if ifPDFAllowed(soup):
                extractPDF(url, soup)
            
            saveXML(response,soup) 
    else:
        print('Not good')


    time.sleep(10)  # variable delay, just maintain 10s overall


if __name__ == '__main__':
    #TODO: get url.txt lines and make handle url
    url_directory = 'urls/'    
    #for urlfile in os.listdir(url_directory):
    urlfile = 'urls-01.txt' # TODO: Change filename here
    print_logs('URL-File Currently Handling: '+ urlfile)
    filepath = os.path.join(url_directory, urlfile) # Make relative path    
    text = open(filepath, 'r')
    data = text.readlines()        
    print(len(data))
    for line in range(len(data)):
        link = data[line].strip().split('\n') # remove '\n' from the url on each line
        itemIdFirst = link[0].split('/')[-2]
        itemIdSecond = link[0].split('/')[-1]
        handleLink = base + 'metadata/handle/'+ itemIdFirst + '/' + itemIdSecond + '/' + 'mets.xml'
        #print(handleLink)
        extractContents(handleLink) # This will bring up metadata page (if exists)
            
    # print(os.listdir(url_directory)[0])
    """    
        Test Intances:
        # Downloadable: https://smartech.gatech.edu/metadata/handle/1853/53031/mets.xml 
        # Not downloadable: https://smartech.gatech.edu/metadata/handle/1853/12889/mets.xml
        # Not Thesis(Book): https://smartech.gatech.edu/metadata/handle/1853/45187/mets.xml
        # Index error: https://escholarship.org/uc/item/0003887p
        # Problematic URL: https://escholarship.org/uc/item/01665550 - Skip if gives 400/500    
    
    testUrl = "https://smartech.gatech.edu/metadata/handle/1853/9360/mets.xml" 
    extractContents(testUrl)
    
    #for line in list(["https://escholarship.org/uc/item/01665550","https://escholarship.org/uc/item/2tk4g64t"]):
    #    link = line.strip().split('\n') # remove '\n' from the url on each line
    #    extractContents(link[0])
    """