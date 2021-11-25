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
    title = soup.find('dim:field',{'element':'title'})
    if title is not None:
        title = title.get_text()

    # Author
    author = soup.find('dim:field',{'element':'creator'})
    if author is not None:
        author = author.get_text()
        if author.find(',') != 1:
            author = author.split(',')[:2]
            author = ",".join(author)

    # Advisor
    advisor = soup.find('dim:field',{'qualifier':'committeeChair'})
    advisor = soup.find('dim:field',{'qualifier':'advisor'})
    if advisor is not None:
        advisor = advisor.get_text()
        if advisor.find(',') != 1:
            advisor = advisor.split(',')[:2]
            advisor = ",".join(advisor)
    ## If advisor is absent and committechair presents
    committechair = soup.find('dim:field',{'qualifier':'committeeChair'})
    if advisor is None and committechair is not None:
        advisor = committechair.get_text()

    # Abstract
    abstract = soup.find('dim:field',{'qualifier':'abstract'})
    if abstract is not None:
        abstract = abstract.get_text()

    # Landing Page URL
    url = soup.find('dim:field',{'qualifier':'uri'})
    if url is not None:
        url = url.get_text()

    # Year
    date = soup.find('dim:field',{'qualifier':'issued'})
    if date is not None:
        date = date.get_text()
        if date.find('-'):
            date = date.split('-')[0]
        
        # Fixing dates on edge cases
        date = re.search(r'[0-9]+', str(date))
        date = date[0]

    # University
    university = soup.find('dim:field',{'qualifier':'grantor'})
    if university is not None:
        university = university.get_text()
    if university is None:
        university = "University of Illinois at Urbana-Champaign"

    # Degree
    degree = soup.find('dim:field',{'qualifier':'name', 'element':'degree'})
    if degree is not None:
        degree = degree.get_text().split(' ')[0]

    # Language
    language = soup.find('dim:field',{'element':'language'})
    if language is not None:
        language = language.get_text()

    # Department
    department = soup.find('dim:field',{'qualifier':'department'})
    if department is not None:
        department = department.get_text()

    # Discipline
    discipline = soup.find('dim:field',{'qualifier':'discipline', 'element':'degree'})
    if discipline is not None:
        discipline = discipline.get_text()

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

def insertPDFs(soup, etdid, etdPath):
    # Get the url from XML
    urlInitials = 'https://www.ideals.illinois.edu/bitstream/handle/'
    url = soup.find('dim:field',{'qualifier':'uri'})
    url = url.get_text()
    identityNumber1 = url.split('/')[-2]
    identityNumber2 = url.split('/')[-1]

    # Use pdfs on directory, get the names and create downloadable url
    pdfName = str(etdPath).split('\\')[-1]
    downloadUrl = urlInitials + identityNumber1 + '/' + identityNumber2 + '/' + pdfName
    print('Download Page:', downloadUrl)
    
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

def moveFileToProductionRepo(xmlPath, etdPath, dbETDId):      
    prodDir = os.path.join('../../', 'etdrepo')     
    firstLevelDir = firstLevelDirCalculation(dbETDId)
    secondLevelDir = secondLevelDirCalculation(dbETDId)

    etdFinalProdDir = prodDir+'/'+firstLevelDir+'/'+secondLevelDir
    """
        Fixing the names of the files in production directory
    """
    etdProduction = etdFinalProdDir + '/' + str(dbETDId) + '.pdf' 
    metadataProduction = etdFinalProdDir + '/' + str(dbETDId) + '.xml' 
    
    if not os.path.isdir(etdFinalProdDir):
        print('enter '+etdFinalProdDir)
        os.makedirs(etdFinalProdDir) 
    
    if etdPath is not None:
        copyfile(etdPath, etdProduction)

    if xmlPath is not None:
        copyfile(xmlPath, metadataProduction)

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
    harvestDirectory = 'harvest/2142'
    print(harvestDirectory)
    etddirs = os.listdir(harvestDirectory)
    etddirs = handleSuddenStop(etddirs,'91813') #TODO: Change here to handle sudden production stop   #metadc53494

    print("#ETDs:", len(etddirs))
    for etddir in etddirs:
        print('')
        # print("Current ETD:", etddir)
        # if etddir == '91825':
        #     continue
        """
            Step 1: Read the files [Directory path may vary based on arrangement]
        """

        xmlFilePath = os.path.join(harvestDirectory+'/'+etddir,etddir+'.xml')
        # Get the pdf. Can be with any name
        etdPath = None
        _etdPath = Path(harvestDirectory+'/'+etddir)
        if any(files.endswith(".pdf") for files in os.listdir(_etdPath)):        
            print("ETD with PDF:", etddir)
            for item in _etdPath.glob('*.pdf'): # Return a list
                etdPath = item

            # Extract and insert table
            xmlfile = open(xmlFilePath, "r")
            soup = BeautifulSoup(xmlfile, 'lxml')

            etdid = insertETDs(soup) 
            #etdid = 30400
            print('DB ID:',etdid)
            insertSubjects(soup, etdid)
            insertPDFs(soup, etdid, etdPath)            

            """
                Step 3: Shift the ETD to the production repo, rename & place file/folders based on ID
            """
            moveFileToProductionRepo(Path(xmlFilePath), etdPath, etdid) #Works
            #break # Loop breaks after a run for now
        

if __name__ == '__main__':
    main()