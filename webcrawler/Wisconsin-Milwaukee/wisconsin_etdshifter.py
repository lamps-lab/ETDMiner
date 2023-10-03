"""
    This script will run on Giacconi server since it(server) has the production repository and 
    will call hwaking from there.
"""
import json
import os
import mysql.connector
from bs4 import BeautifulSoup
from shutil import copyfile
import xml.etree.ElementTree as ET
import urllib.request
import urllib.response
import urllib.parse
import re

config = {
    'user': 'uddin',
    'password': 'TueJul271:56:04PM',
    'host': 'hawking.cs.odu.edu',
    'database': 'pates_etds'
}

import time
import ssl
from socket import timeout
# Bypassing SSL verification check
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def secondLevelDirCalculation(dbETDId):
    """
        Second level will be 4 digit number -> 0000 , 0001 .......9999
        So after getting residue wiith 10000, we need to decide how many 0 to append at front
    """
    secondLevelDir = ''
    number = int(dbETDId)%10000    
    totalDigits = len(str(number))
    if totalDigits == 1:
        secondLevelDir = '000' + str(number)
    elif totalDigits == 2:
        secondLevelDir = '00' + str(number)
    elif totalDigits == 3:
        secondLevelDir = '0' + str(number)
    else:
        secondLevelDir = str(number)

    return secondLevelDir

def firstLevelDirCalculation(dbETDId):
    """
        First level will be 3 digit number -> 000 , 001 , 002, 003 .......010
        So after dividing wiith 10000, we need to decide how many 0 to append at front
    """
    firstLevelDir = ''
    number = int(dbETDId)//10000    
    totalDigits = len(str(number))
    if totalDigits == 1:
        firstLevelDir = '00' + str(number)
    elif totalDigits == 2:
        firstLevelDir = '0' + str(number)
    else:
        firstLevelDir = str(number)

    return firstLevelDir
   

def insertSubjects(soup, etdid):    
    # Subjects
    subjectXml = soup.find_all('dim:field',{'element':'subject'})
    subjects = []
    if subjectXml:
        for item in subjectXml:
            subjects.append(item.get_text())

    if not subjects:
        subjects = None

    print('Subject(s):', subjects)
    
    """
        Database insertion for Subjects table
    """
    if subjects:
        for subject in subjects:
            db_connection = mysql.connector.connect(**config)
            mycursor = db_connection.cursor()

            sql = "INSERT INTO subjects (etdid, subject) VALUES (%s, %s)"
            val = (etdid, subject)
            mycursor.execute(sql, val)
            db_connection.commit()

            mycursor.close()
            db_connection.close()

def insertETDs(soup):
    """
        Extract values first
    """
    # Title
    title = soup.find('div',{'id':'title'})
    
    if title is not None:
        title = title.find('p').get_text()

    # Author
    author = soup.find('div',{'id':'authors'})
    if author is not None:
        author = author.find('p',{'class':'author'}).find('a').find('strong').get_text()
        # if author.find(',') != 1:
        #     author = author.split(',')[:2]
        #     author = ",".join(author)
   
    # Advisor
    advisor = soup.find('div',{'id':'advisor1'})
    if advisor is not None:
        advisor = advisor.find('p').get_text()
   
    # print(advisor)
    # Abstract
    abstract = soup.find('div',{'id':'abstract'})
    if abstract is not None:
        abstract = abstract.find('p').get_text()
    
    # Landing Page URL
    url = soup.find('div',{'id':'recommended_citation'})
    if url is not None:
        url = ''.join(url.find('p').find('br').next_siblings)
   
    # Year
    date = soup.find('div',{'id':'publication_date'})
    if date is not None:
        date = str(date.find('p').get_text())
        if ('-'in date):
            sizel=len(date.split('-'))
            date = date.split('-')[sizel-1]
        else:
            date = date.split(' ')[1]
       
  
    # University
    university = "University of Wisconsin-Milwaukee"
    # if university is not None:
    #     university = university.get_text()
    
    # Degree
    degree = soup.find('div',{'id':'degree_name'})
    if degree is not None:
        degree = degree.find('p').get_text()
    
    # Language
    language = 'en'
    # if language is not None:
    #     language = language.get_text()

    # Department
    department = soup.find('div',{'id':'department'})
    if department is not None:
        department = department.find('p').get_text()
    
    # Discipline
    discipline = soup.find('dim:field',{'qualifier':'discipline', 'element':'degree'})
    if discipline is not None:
        discipline = discipline.get_text()
    else:
        discipline = "Not Found"

    print('Title:', title)
    print('Author:', author)
    print('Advisor:', advisor)
    print('Abstract:', abstract)
    print('Date:', date)
    print('University:', university)
    print('Degree:', degree)
    print('URL:', url)
    print('Language:', language)
    print('Department:', department)
    print('Discipline:', discipline)

    """
        Database insertion for ETD table
    """
    # Setup Database connection
    db_connection = mysql.connector.connect(**config)
    # Insert values to database
    mycursor = db_connection.cursor()
    sql = "INSERT INTO etds (title, author, advisor, year, university, URI, department, degree, discipline, language, abstract) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (title, author, advisor, date, university, url, department, degree, discipline, language, abstract)
    mycursor.execute(sql, val)
    db_connection.commit()

    etdId = mycursor.lastrowid
    mycursor.close()
    db_connection.close()

    return etdId

def insertPDFs(soup, etdid, etdPath, etd_number):
    # Get the url from XML
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
    urlInitials = hrefValue
    print("urlIn: ", urlInitials)
    # url = soup.find('dim:field',{'qualifier':'uri'})
    # url = url.get_text()
    # identityNumber1 = url.split('/')[-2]
    # identityNumber2 = url.split('/')[-1]

    # Use pdfs on directory, get the names and create downloadable url
    pdfName = str(etdPath).split('\\')[-1]
    downloadUrl = urlInitials 
    
    """
         Database insertion for PDFs table
    """
    firstLevelDir = firstLevelDirCalculation(etdid)
    secondLevelDir = secondLevelDirCalculation(etdid)

    localrelpath = firstLevelDir+'/'+secondLevelDir
    db_connection = mysql.connector.connect(**config)
    mycursor = db_connection.cursor()

    sql = "INSERT INTO pdfs (etdid, url, localrelpath) VALUES (%s, %s,%s)"
    val = (etdid, downloadUrl, str(localrelpath))
    mycursor.execute(sql, val)
    db_connection.commit()

    mycursor.close()
    db_connection.close()

def moveFileToProductionRepo(etdPath, dbETDId):      
    prodDir = os.path.join('../', 'etdrepo')     
    firstLevelDir = firstLevelDirCalculation(dbETDId)
    secondLevelDir = secondLevelDirCalculation(dbETDId)

    etdFinalProdDir = prodDir+'/'+firstLevelDir+'/'+secondLevelDir
    etdProduction = etdFinalProdDir + '/' + str(dbETDId) + '.pdf' 
    print(etdFinalProdDir)
    if not os.path.isdir(etdFinalProdDir):
        os.makedirs(etdFinalProdDir) 
    
    if etdPath is not None:
        copyfile(etdPath, etdProduction)
       
def movehtml(htmlpath, dbETDId):
    prodDir = os.path.join('../', 'etdrepo')     
    firstLevelDir = firstLevelDirCalculation(dbETDId)
    secondLevelDir = secondLevelDirCalculation(dbETDId)

    etdFinalProdDir = prodDir+'/'+firstLevelDir+'/'+secondLevelDir
    etdProduction = etdFinalProdDir + '/' + str(dbETDId) + '.html' 
    print(etdFinalProdDir)
    if not os.path.isdir(etdFinalProdDir):
        os.makedirs(etdFinalProdDir) 
    
    if htmlpath is not None:
        copyfile(htmlpath, etdProduction)
"""
    This method finds where the code stoped and helps to resume from these
"""
def handleSuddenStop(etddirs, stoppedDir):
    n = 0
    for item in etddirs:        
        if item == stoppedDir:
            break
        n = n+1

    return etddirs[n:]

from pathlib import Path
def main():    
    """
    Step 1: File read
    Step 2: Extract info from xml
    Step 3: Populate 3 tables
    Step 4: Shift files to production repo 
    """
    harvestDirectory = 'Wisconsin_ETDs'
    print(harvestDirectory)
    etddirs = os.listdir(harvestDirectory)
    print(etddirs)
    #etddirs = handleSuddenStop(etddirs,'metadc278485') #TODO: Change here to handle sudden production stop   #metadc53494

    print("#ETDs:", len(etddirs))
    for i in range(548,2856):
        print('')
        print("Current ETD:", i)
        # if etddir == '1911':
        #     continue
        """
            Step 1: Read the files [Directory path may vary based on arrangement]
        """

        xmlFilePath = os.path.join(harvestDirectory+'/'+str(i),str(i)+'.html')

        # Get the pdf. Can be with any name
        # etdPath = None
        _etdPath = Path(harvestDirectory+'/'+str(i))
        for item in _etdPath.glob('*.pdf'): # Return a list
            etdPath = item

        # Extract and insert table
            if os.path.exists(xmlFilePath):

                xmlfile = open(xmlFilePath, "r")
                soup = BeautifulSoup(xmlfile, 'lxml')
                # print(soup)
                etdid = insertETDs(soup) # DONE
                # insertSubjects(soup, etdid) # DONE
                insertPDFs(soup, etdid, etdPath, str(1001+i-1)) # Done
                

                """
                    Step 3: Shift the ETD to the production repo, rename & place file/folders based on ID
                """
                print("etdpath",etdPath)
                moveFileToProductionRepo(etdPath, etdid) #Works
                #break # Loop breaks after a run for now
            else:
                pass
        for item in _etdPath.glob('*.html'): # Return a list
            htmlPath = item

        # Extract and insert table
            if os.path.exists(xmlFilePath):

                

                """
                    Step 3: Shift the ETD to the production repo, rename & place file/folders based on ID
                """
                print("path: ",htmlPath)
                movehtml(htmlPath, etdid) #Works
                #break # Loop breaks after a run for now
            else:
                pass
                

if __name__ == '__main__':
    main()