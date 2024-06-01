#!/usr/bin/env python
# coding: utf-8

# # Harvest ETDs from an OAI-PMH provider  
# 
# Bill Ingram <waingram@vt.edu>  
# February 2, 2021  
# 

# This code uses an OAI-PMH harvester library for Python called [Sickle](https://sickle.readthedocs.io/). To install, run ```pip install sickle``` or ```conda install -c bioconda sickle```.  

# In[1]: 


from sickle import Sickle


# First, find the URL of the OAI-PMH endpoint, but make sure this is the endpoint for just the ETD collection and not the entire repository. 
#   
# For instance, on the CMU repository, we use the URL ```https://api.figshare.com/v2/oai?verb=ListRecords&metadataPrefix=mets&set=item_type_8```.  
#   
#   
# Notice the parameters:  
# ```verb=ListRecords``` -- list all the records  
# ```metadataPrefix=mets``` -- list the records in METS XML format (this is better than `oai-dc` but not all repositories support METS.  
# ```set=item_type_8``` -- on this particular repository, this is the `set` containing ETDs 

# In[2]:http://d-scholarship.pitt.edu/cgi/oai2


# sickle = Sickle('https://www.ideals.illinois.edu/dspace-oai/request?')
sickle = Sickle('https://www.ideals.illinois.edu/oai-pmh')
# records = sickle.ListRecords(metadataPrefix='dim', set='com_2142_5130')
records1 = sickle.ListRecords(metadataPrefix='oai_dc', set='col_2142_5128')
records2 = sickle.ListRecords(metadataPrefix='oai_dc', set='com_2142_5130')

# records = list(records1) + list(records2)
# Before starting, make sure to check the server's robots.txt file and obey all restrictions and limits. If the ```crawl-delay``` directive is set, copy the value to a local variable. 


crawl_delay = 0


# Convenience function for downloading files:



import requests
import cgi
import time
from random import randint
import urllib.request
import urllib.response
import urllib.parse
import bs4
import ssl
from socket import timeout

"""
    #### Utility Modules ####
"""
"""
    
"""
def getPDFdownloadUrl(soup):
    hrefValue = None
    # findClassess = soup.find_all('tr', {'class':'ds-table-row odd'})
    
    # @Dennis
    findClassess = soup.find('div', {'class': 'container-fluid'})   
    if findClassess:       
        findPage = findClassess.find('div',{'class':'page-content'})        
        if findPage:  
            print('find findPage')              
            findFile = findPage.find('div', {'id':'file-navigator'})            
            if findFile:
                print("find findFile")   
                print(findFile)             
                findColumn = findFile.find('div',{'id':'file-navigator-thumbnail-column'})                
                if findColumn:
                    print("find Column")
                    
                
                    findDivLast = findFile.find('div',{'class':'dropdown-menu'})
                    
                    if findDivLast:
                        print("find last")
                        
                        findA = findDivLast.find('a',{'id':'copy-link'})
                
                
                    if findA and findA['data-bitstream-url']:
                        hrefValue = findA['data-bitstream-url']                  
                        # Check if there is download permission
                        if 'isAllowed=n' in hrefValue:
                            hrefValue = None
                
        
                # if findClass:
            #     imgTag = findClass.find('img')
            #     if imgTag['title'] == "application/pdf":
            #         anchortag = findClass.find('a')
            #         if anchortag:
            #             print(anchortag)
            #             hrefValue = anchortag['href']
            #             hrefValue = "https://www.ideals.illinois.edu/" + hrefValue
            #             # Check if there is download permission
            #             if 'isAllowed=n' in hrefValue:
            #                 hrefValue = None
            #             break
            
                
                # if a_element and a_element.find('i', {'clsss':'fa fa-download'}):
                #     hrefValue = a_element['href']
                #     hrefValue = "https://www.ideals.illinois.edu/" + hrefValue
                #     # Check if there is download permission
                #     if 'isAllowed=n' in hrefValue:
                #         hrefValue = None
                #         break

    return hrefValue

"""
    This module will help keep the op running just incase any URL error occurs
"""
def isPDFDownloadUrlWorkable(soup):
    downloadableUrl = getPDFdownloadUrl(soup)
    print('downloadableUrl: ',downloadableUrl)

    if downloadableUrl is None: # Special Case: PDF link is not available at all
        return False
    
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

# Bypassing SSL verification check
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def download_file_stream(url, path, crawl_delay=0, allow_redirects=True):
    """Download a file from the landing page of the particular ETD. It handles redirects and it will
        try to figure out the filename if unknown. 
        
        Returns path to downloaded file. 
        
        Arguments:
        url            : URL for the landing page 
        path           : pathlib.Path object -- Where you want the file to be saved
        crawl_delay    : How long to delay before downloading 
        allow_redirects: (boolean) Allow redirects or not
    """
    time.sleep(crawl_delay)

    filename = ''
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
        print(url,"download worked!!")
        response = response.read()
        soup = bs4.BeautifulSoup(response, "html.parser")

        #If PDF not allowed of available, just take the XML
        if isPDFDownloadUrlWorkable(soup):

            # get the filename -- this might not always work
            downloadableUrl = getPDFdownloadUrl(soup)
            filename = downloadableUrl.split('/')[-1]
            filename = filename.split('?')[0]
            filename = filename.replace('.pdf','')
            # Get the PDF
            response = urllib.request.urlopen(downloadableUrl,context=ctx)

            # save the file
            filename = filename + '.pdf' # Removing and adding just to be safe
            with open(path / filename, 'wb') as f:
                f.write(response.read())
        else:
            print("isPDFDownloadUrlWorkable is false")
    return (path / filename)


# Iterate over the records: 
#  - Get the identifier  
#  - Create directory based on identifier  
#  - Save descriptive metadata as XML  
#  - Save content file(s) 


from pathlib import Path
from lxml import etree

print("strat for loop 1")
for record in records1:
    tree = etree.fromstring(record.raw)

    # get the identifier and make dirs 
    identifiers = tree.xpath('//oai:identifier', namespaces={'oai': 'http://www.openarchives.org/OAI/2.0/'})
    identifier = identifiers[0].text
    identifier = identifier.split(':')[-1]
    pathname = identifier

    p = Path('harvest') / pathname
    p = p.resolve()

    # if the directory already exists, assume we already got this one and skip to next
    if p.is_dir(): 
        continue
    
    # otherwise, create the directory
    p.mkdir(parents=True, exist_ok=True)

    # write desc metadata to file
    # metadatas = tree.xpath('//dim:dim', namespaces={'dim': 'http://www.dspace.org/xmlns/dspace/dim'})
    # for metadata in metadatas:
    #     filename = identifier.split('/')[-1].lower() + '.xml'
    #     (p / filename).open('wb').write(etree.tostring(metadata, pretty_print=True))

    # # download content files
    # files = tree.xpath('//dim:field[@element="identifier" and @qualifier="uri"]', namespaces={'dim': 'http://www.dspace.org/xmlns/dspace/dim'})
    
    # @Dennis change all the dim to oai_dc
    metadatas = tree.xpath('//oai_dc:dc', namespaces={'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/'})
    for metadata in metadatas:
        filename = identifier.split('/')[-1].lower() + '.xml'
        (p / filename).open('wb').write(etree.tostring(metadata, pretty_print=True))
        
        # @Dennis re-write the pdf download logic
        # url = "http://hdl.handle.net/" + identifier
        
        # print('download pdf Now on:',url)
        # filename = download_file_stream(url, p, crawl_delay=crawl_delay)
        # if filename is None:
        #     print(f'There was a problem downloading {url}')
        

    # # download content files
    # files = tree.xpath('//oai_dc:dc/oai_dc:identifier', namespaces={'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/'})
    
    # print('files',files)

    # for url in files:
    #     etdLandingPage = url.xpath("string()")
    #     print('Now on:',etdLandingPage)
    #     filename = download_file_stream(etdLandingPage, p, crawl_delay=crawl_delay)
    #     if filename is None:
    #         print(f'There was a problem downloading {url}')


print("strat for loop 2")
for record in records2:
    tree = etree.fromstring(record.raw)

    # get the identifier and make dirs 
    identifiers = tree.xpath('//oai:identifier', namespaces={'oai': 'http://www.openarchives.org/OAI/2.0/'})
    identifier = identifiers[0].text
    identifier = identifier.split(':')[-1]
    pathname = identifier

    p = Path('harvest1') / pathname
    p = p.resolve()

    if p.is_dir(): 
        continue
    
    # otherwise, create the directory
    p.mkdir(parents=True, exist_ok=True)

    metadatas = tree.xpath('//oai_dc:dc', namespaces={'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/'})
    for metadata in metadatas:
        filename = identifier.split('/')[-1].lower() + '.xml'
        (p / filename).open('wb').write(etree.tostring(metadata, pretty_print=True))
        
  

        

