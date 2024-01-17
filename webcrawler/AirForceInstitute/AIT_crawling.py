"""
    This program will go through the url-<Num>.txt files and -
    1. download pdf 
    2. extract metadata from html
"""
# University of Massachusettes Amherst
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
import wget


base = "https://scholar.afit.edu/etd/"
not_found = 0
# Bypassing SSL verification check
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Log stuffs
def print_logs(text):
    print(text)
    with open("log.txt",'a',encoding = 'utf-8') as f:
        f.write(text+"\n")
        
# @Dennis add print_download_PDF_error_logs       
def print_download_PDF_error_logs(text):
    print(text)
    with open("download_PDF_error_log.txt",'a',encoding = 'utf-8') as f:
        f.write(text+"\n")
        
# @Dennis add print_download_Matadata_error_logs        
def print_download_Matadata_error_logs(text):
    print(text)
    with open("download_Matadata_error_log.txt",'a',encoding = 'utf-8') as f:
        f.write(text+"\n")

"""
    This module will help keep the op running just incase any URL error occurs
"""
def isPDFDownloadUrlWorkable(soup):
    downloadableUrl = getPDFdownloadUrl(soup)
    print("downloadable=========", downloadableUrl)
    isWorkable = True
    try:
        if(downloadableUrl == None):
            pass
        else:
            response = urllib.request.urlopen(downloadableUrl)
            print("response", response)
        
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

# def ifPDFAllowed(soup):
#     allowed = False
#     hrefValue = ""
#     # If PDF avalilable
#     if soup.find('mets:file',mimetype="application/pdf"):
#         hrefValue = soup.find('mets:file',mimetype="application/pdf").find('mets:flocat')['xlink:href']
#     yFound =  re.search(r"(isAllowed=y)+", hrefValue)    
    
#     if yFound is not None:
#         allowed = True
    
#     return allowed

def getPDFdownloadUrl(soup):
    if (soup.find('div',{'id':'beta_7-3'})== None):
       anchortag = None
    else:
        if(soup.find('div',{'id':'beta_7-3'}).find('div',{'class':'aside download-button'})== None):
            anchortag = None
        else:
            anchortag = soup.find('div',{'id':'beta_7-3'}).find('div',{'class':'aside download-button'})
    if anchortag == None:
        hrefValue = None
    else:
        hrefValue = anchortag.find('a') #soup.find('mets:file',mimetype="application/pdf").find('mets:flocat')['xlink:href']
        if hrefValue == None:
            pass
        else:
            hrefValue = anchortag.find('a')['href']
    #@Dennis downloadableUrl = urllib.parse.urljoin(base, hrefValue)  
    return hrefValue

# Check if it is a thesis [from breadcrumb]
def isItemThesis(soup):
    isThesis = False

    contentTypes = soup.find("div",class_="crumbs").find_all("a",class_="ignore").text()
    
    length = len(contentTypes)
    print("contentTypes[0].text",contentTypes[0].text)
    
    if ("ETD" in contentTypes[2].text and length == 4):
        isThesis = True
        

    # print("Content types:", contentTypes)
    # for contentType in contentTypes:
    #     contentTypeText = contentType.get_text()
    #     if re.match("(Dissertation)+", contentTypeText) or re.match("(Thesis)+", contentTypeText) or re.match("(Theses and Dissertations)+", contentTypeText):
    #         isThesis = True

    return isThesis

def extractPDF(url,soup, j):
    # Get the PDF download-able URL
    downloadableUrl = getPDFdownloadUrl(soup)
    # print("downloadable=========", downloadableUrl)
    # Extract item id    
    #@Dennis itemId = url.split("/")[-1]
    itemId = url.rstrip('/').split('/')[-1]
    
    print("I am item",itemId)

    """
        TODO: Download and store the PDF. [Make sure folder with ID exists]        
        etds -> <itemID[D]> -> itemID.pdf | itemID.html
    """
    # Create directory based on item-id
    directory = 'AIT_ETDs/'+ j + '/'
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Download and store pdf to that directory
    fileName = j + '.pdf'
    filepath = os.path.join(directory, fileName)     
    
    # print("filepath",filepath)   
    # print("os.getcwd(): ", os.getcwd())
    #urllib.request.urlretrieve(downloadableUrl,filepath) # urllib.request.urlretrieve(source,dest)
    
    # @Dennis add: or  os.path.exists(fileName), if the pdf already exist, do not re-download again
    print("os.path.exists(filepath): ",os.path.exists(filepath))
    # @Dennis add print_download_PDF_error_logs
    # downloadableUrl = None   //used for test when downloadableUrl is None, the print log is correct
    if downloadableUrl == None or os.path.exists(filepath):
        if downloadableUrl == None:
            print("downloadableUrl is None")
            print_download_PDF_error_logs(""+j+".pdf is not downloadable, because the downloadableUrl is None")
        else:
            print(filepath," aleady exist, pass")
    else:        
        try:
            response = urllib.request.urlopen(downloadableUrl, context=ctx)

            # If the URL was successfully opened, proceed with writing the file and other processing steps
            with open(filepath, 'wb') as f:
                f.write(response.read())

            print("Successful pdf parsing for:", itemId)

        except urllib.error.HTTPError as e:
            print("HTTP Error:", e)
            print_download_PDF_error_logs(""+j+".pdf is not downloadable, because HTTP Error:"+ e )
        except urllib.error.URLError as e:
            print("URL Error:", e)
            print_download_PDF_error_logs(""+j+".pdf is not downloadable, because URL Error:"+ e )
        except urllib.error.ContentTooShortError as e:
            print("Content Too Short Error:", e)
            print_download_PDF_error_logs(""+j+".pdf is not downloadable, because Content Too Short Error:"+ e )
        except ConnectionResetError as e:
            print("Connection Reset Error:", e)
            print_download_PDF_error_logs(""+j+".pdf is not downloadable, because Connection Reset Error:"+ e )
        except timeout:
            print("Timeout Error")
            print_download_PDF_error_logs(""+j+".pdf is not downloadable, because Timeout Error" )
        except Exception as e:
            print("An unexpected error occurred:", e)   
            print_download_PDF_error_logs(""+j+".pdf is not downloadable, because An unexpected error occurred:" +e)  
        
    #@Dennis adding errors handling for urlopen 
    #     response = urllib.request.urlopen(downloadableUrl,context=ctx)
    #     with open(filepath, 'wb') as f:        
    #         f.write(response.read())
    # # wget.download(downloadableUrl,"Users/lamiasalsabil/Downloads/1234.pdf")
    #     print("Successful pdf parsing for:"+itemId)

def saveHTML(url,response,soup, j):
    # Extract item id
    #objId = soup.find('mets:mets')['objid']    
    # Create directory based on item-id
    directory = 'AIT_ETDs/'+ j+ '/'
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Define filename with item-id
    fileName = j + '.html'
    filepath = os.path.join(directory, fileName)  
    
    # @Dennis add if condiction
    if not os.path.exists(filepath):
    #print(response.decode('utf-8'))
    # @Dennis Handle the matadata download error, and print the error log
        try:            
            with open(filepath, 'wb') as file: # wb for override
                file.write(response)
            print("Successful save matadata:", fileName)
        except urllib.error.HTTPError as e:
            print("HTTP Error:", e)
            print_download_Matadata_error_logs(""+fileName+" is not saved, because HTTP Error:"+ e )
        except urllib.error.URLError as e:
            print("URL Error:", e)
            print_download_Matadata_error_logs(""+ fileName +" is not saved, because URL Error:"+ e )
        except urllib.error.ContentTooShortError as e:
            print("Content Too Short Error:", e)
            print_download_Matadata_error_logs(""+ fileName +" is not saved, because Content Too Short Error:"+ e )
        except ConnectionResetError as e:
            print("Connection Reset Error:", e)
            print_download_Matadata_error_logs(""+ fileName +" is not saved, because Connection Reset Error:"+ e )
        except timeout:
            print("Timeout Error")
            print_download_Matadata_error_logs(""+ fileName +" is not saved, because Timeout Error" )
        except Exception as e:
            print("An unexpected error occurred:", e)   
            print_download_Matadata_error_logs(""+ fileName +" is not saved, because An unexpected error occurred:" +e) 
    else:
        print(filepath,"already exsit, pass")

def extractContents(url, j):             
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
        
        response = response.read()
        soup = bs4.BeautifulSoup(response, "html.parser")
        
        #print(soup)
        #Check If item is thesis & PDF is download-able => then we'll do extraction
        print_logs("Now starting: "+ url)  
        print_logs("It's thesis")    
        if isPDFDownloadUrlWorkable(soup):                                
            extractPDF(url, soup, j) # Completed            
        saveHTML(url,response,soup,j)       
        # if isItemThesis(soup):
        #     print_logs("It's thesis")    
        #     if isPDFDownloadUrlWorkable(soup):                                
        #         extractPDF(url, soup) # Completed            
        #     saveHTML(url,response,soup) 
    else:
        global not_found
        not_found += 1
        print('Not good')


    time.sleep(5)  # variable delay, just maintain 10s overall


if __name__ == '__main__':  

    #TODO: get url.txt lines and make handle url 
    #for urlfile in os.listdir(url_directory):
    #@Dennis for j in range(3416,5431):
    for j in range(1,6298):
        url = base+str(j)+'/'
        
        extractContents(url, str(j))
        print('ETD number:', j)
    print("NOT Found ETDs: ", not_found)
       
            
  
