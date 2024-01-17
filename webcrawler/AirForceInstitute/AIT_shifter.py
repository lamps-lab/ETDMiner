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
import requests

#@Dennis
# config = {
#     'user': 'uddin',
#     'password': 'TueJul271:56:04PM',
#     'host': 'hawking.cs.odu.edu',
#     'database': 'pates_etds'
# }

config = {
    'user': 'Dennis',
    'password': '1234',
    'host': 'localhost',  # or '127.0.0.1'
    'database': 'testdb' 
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

# @Dennis create a new funciton to check if the record exists in the database
def exists_in_etds(soup):
    data = extract_all_field(soup)
    title = data.get('title')
    pri_identifier = data.get('pri_identifier')
    second_identifier = data.get('second_identifier')
    # print(f"exists_in_etds: title:{title}, pri_identifier: {pri_identifier} ")
    
    db_connection = mysql.connector.connect(**config)
    mycursor = db_connection.cursor()

    etd_id = None

    # Check if pri_identifier exists
    query = "SELECT id FROM etds WHERE pri_identifier = %s"
    params = (pri_identifier,)
    mycursor.execute(query, params)
    result = mycursor.fetchone()

    if result:
        # pri_identifier exists
        etd_id = result[0]
        print("pri_identifier exists ")

    # If pri_identifier does not exist, check second_identifier
    elif not etd_id:
        query = "SELECT id FROM etds WHERE second_identifier = %s"
        params = (second_identifier,)
        mycursor.execute(query, params)
        result = mycursor.fetchone()

        if result:
            # second_identifier exists
            etd_id = result[0]
            print("second_identifier exists ")

    # If both pri_identifier and second_identifier do not exist, check title
    elif not etd_id:
        query = "SELECT id FROM etds WHERE trim(title) = trim(%s)"
        params = (title,)
        mycursor.execute(query, params)
        result = mycursor.fetchone()

        if result:
            # title exists
            etd_id = result[0]
            print("title exists ")

    # No match found for any identifier
    mycursor.close()
    db_connection.close()    
    
    return etd_id
    

# @Dennis create a new funciton used to check if this record has any empty field
def empty_fields(soup,etdid):
    required_fields = [
        'title', 'author', 'advisor', 'year', 'university', 'URI', 'department', 'degree', 'discipline', 'language', 'abstract', 'copyright', 'pri_identifier', 'second_identifier', 'haspdf', 'timestamp_metadata','timestamp_pdf'
    ]
    
    empty_fields = []

    db_connection = mysql.connector.connect(**config)
    mycursor = db_connection.cursor()

    for field in required_fields:
        query = f"SELECT COUNT(*) FROM etds WHERE id = {etdid} and {field} IS NULL "
        mycursor.execute(query)
        result = mycursor.fetchone()

        if result[0] > 0:
            empty_fields.append(field)

    mycursor.close()
    db_connection.close()

    return empty_fields
    
# @Dennis  create a new function used to update the empty field
def update_empty_field(soup,empty_list,etdid) :
    data = extract_all_field(soup)
    db_connection = mysql.connector.connect(**config)
    mycursor = db_connection.cursor()
    print("start update empty feild")
    for field in empty_list:
        value = data.get(field)
        if value is not None:
            # Update the field in the etds table
            query = f"UPDATE etds SET {field} = %s WHERE id = {etdid}"
            params = (value,)
            mycursor.execute(query, params)
            db_connection.commit()
            print(f"updated the field {field}: {value}")
    mycursor.close()
    db_connection.close()     
    
           
# @Dennis create a new function extract_all_field, used to extract all field from matadata, and return a JSON.
def extract_all_field(soup):
     # Title
    title = soup.find('div',{'id':'title'})
    # print("title: ",title)
    if title is not None:
        #@Dennis title = title.find('p').get_text()
        title = title.find('a').get_text()
        print("title: ",title)

    # Author
    author = soup.find('div',{'id':'authors'})
    if author is not None:
        author = author.find('p',{'class':'author'}).find('a').find('strong').get_text()
        print("author: ",author)
        # if author.find(',') != 1:
        #     author = author.split(',')[:2]
        #     author = ",".join(author)
   
    # Advisor
    advisor = soup.find('div',{'id':'advisor1'})
    if advisor is not None:
        advisor = advisor.find('p').get_text()
        print("advisor: ",advisor)
   
    # print(advisor)
    # Abstract
    abstract = soup.find('div',{'id':'abstract'})
    if abstract is not None:
        abstract = abstract.find('p').get_text()
        print("abstract: ", abstract)
    
    # Landing Page URL
    url = soup.find('div',{'id':'recommended_citation'})
    if url is not None:
        # url = ''.join(url.find('p').find('br').next_siblings)
        #Dennis url = url.find('p').find('br').find_next_sibling().get_text()
        url_p = url.find('p')
        url_br = url_p.find('br')
        # print("url_br: ",url_br)
        # url_final = url_br.find_next_sibling(text = True)
        url_final = url_br.find_next_sibling(string = True)
        # print("url_final: ",url_final)
        url = url_final.strip()
        print("url: ",url)
   
    # Year
    date = soup.find('div',{'id':'publication_date'})
    try:
        if date is not None:
            date = date.find('p').get_text()
            if len(date.split('-'))==3:
                date=date.split('-')
                date = date[2]
            elif len(date.split('-'))==2:
                date=date.split('-')
                date = date[1]
            else:
                date = date.split(' ')[1]
    except:
        pass
       
  
    # University
    university = "Air Force Institute of Technology"
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
    
    discipline = soup.find('div',{'id': 'bp_categories'})
    if discipline is not None:
        try:
            discipline = discipline.find('p').get_text()
        except:
            discipline = None
    else:
        discipline = None
        
        
    # CopyRight link @Dennis
    copyright_link = soup.find('a',{'title': 'Copyright Policy'})
    if copyright_link is not None:
        try:
            copyright_url = copyright_link.get('href')
        except:
            copyright_url = None
    else:
        copyright_link = None
        
    # CopyRight text @Dennis
    def extract_copyright(url):
        response = requests.get(url)
        if response.status_code == 200:
            content = response.content
            soup = BeautifulSoup(content, 'html.parser')
            copyright_pra = soup.find('div',{'class': 'wpb_wrapper'})
            if copyright_pra is not None:
                paragraphs = copyright_pra.find_all('p')
                copyright = '\n'.join([paragraph.get_text() for paragraph in paragraphs])                
                
                return copyright
            else:
                return None
    copyright = extract_copyright(copyright_url)
    
    # AFIT Designator @Dennis
    AFIT = soup.find('div',{'id':'afit_designator'})
    if AFIT is not None:
        AFIT = AFIT.find('p').get_text()
        
    # DTIC  Accession Number @Dennis
    DTIC = soup.find('div',{'id':'dtic_accession_number'})
    if DTIC is not None:
        DTIC = DTIC.find('p').get_text()
    data = {
        'title': title,
        'author': author,
        'advisor': advisor,
        'abstract': abstract,
        'date': date,
        'university': university,
        'degree': degree,
        'url': url,
        'language': language,
        'department': department,
        'discipline': discipline,        
        'copyright': copyright,
        'pri_identifier': AFIT,
        'second_identifier': DTIC,        
    }
    
    # print(data)
    return data   


def insertETDs(soup):
    """
        Extract values first
    """
   
    """
        Database insertion for ETD table
    """
    # Setup Database connection
    db_connection = mysql.connector.connect(**config)
    # Insert values to database
    mycursor = db_connection.cursor()
    oads_flag = 0
    data = extract_all_field(soup)
    sql = "INSERT INTO etds (title, author, advisor, year, university, URI, department, degree, discipline, language, abstract, oadsclassifier, copyright, pri_identifier, second_identifier) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s)"
    val = (
        data.get('title'), 
        data.get('author'), 
        data.get('advisor'), 
        data.get('date'), 
        data.get('university'), 
        data.get('url'), 
        data.get('department'), 
        data.get('degree'), 
        data.get('discipline'), 
        data.get('language'), 
        data.get('abstract'), 
        data.get('oads_flag'),
        data.get('copyright'),
        data.get('pri_identifier'),
        data.get('second_identifier'),
    )
    
    mycursor.execute(sql, val)
    db_connection.commit()

    etdId = mycursor.lastrowid
    mycursor.close()
    db_connection.close()
    print("etdId: ",etdId)

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
    
# @Dennis create a final_pdf_dir function, used to return a  final directory
def final_pdf_dir(etdid):
    prodDir = os.path.join('../', 'etdrepo')
    firstLevelDir = firstLevelDirCalculation(etdid)
    secondLevelDir = secondLevelDirCalculation(etdid)

    pdf_FinalProdDir = prodDir+'/'+firstLevelDir+'/'+secondLevelDir    
    pdf_path = pdf_FinalProdDir + '/' + str(etdid) + '.pdf'
    return pdf_path

# @Dennis create a final_html_dir(etdid) function, used to return a  final directory
def final_html_dir(etdid):
    prodDir = os.path.join('../', 'etdrepo')
    firstLevelDir = firstLevelDirCalculation(etdid)
    secondLevelDir = secondLevelDirCalculation(etdid)

    html_FinalProdDir = prodDir+'/'+firstLevelDir+'/'+secondLevelDir    
    html_path = html_FinalProdDir + '/' + str(etdid) + '.html'
    return html_path



# @Dennis create a insert_haspdf_timestamp function
from datetime import datetime    
def insert_haspdf_timestamp(final_dir,etdid):
    haspdf = 0
    
    if os.path.exists(final_dir):
        haspdf = 1
        pdf_timestamp = datetime.fromtimestamp(os.path.getmtime(final_dir))    
    
        db_connection = mysql.connector.connect(**config)
        mycursor = db_connection.cursor()

        sql = "update etds set haspdf = %s, timestamp_pdf = %s  where id = %s"
        val = (haspdf, pdf_timestamp, etdid)
        mycursor.execute(sql, val)
        db_connection.commit()

        mycursor.close()
        db_connection.close()
        
    else:
        db_connection = mysql.connector.connect(**config)
        mycursor = db_connection.cursor()

        sql = "update etds set haspdf = %s  where id = %s"
        val = (haspdf, etdid)
        mycursor.execute(sql, val)
        db_connection.commit()

        mycursor.close()
        db_connection.close()
# @Dennis create a insert_metadata_timestamp function    
from datetime import datetime    
def insert_metadata_timestamp(final_dir,etdid):
    if os.path.exists(final_dir):    
        meta_path = final_dir   
        meta_timestamp = datetime.fromtimestamp(os.path.getmtime(meta_path))
        
        db_connection = mysql.connector.connect(**config)
        mycursor = db_connection.cursor()

        sql = "update etds set  timestamp_metadata = %s where id = %s"
        val = ( meta_timestamp, etdid)
        mycursor.execute(sql, val)
        db_connection.commit()

        mycursor.close()
        db_connection.close()
        
# @Dennis create a etdrepo_pdf_check function, used to check if the pdf/html exist in the etdrepo     
def etdrepo_check(final_dir,etdid):
    if os.path.exists(final_dir):
        return 1
    else:
        return None

def moveFileToProductionRepo(etdPath, dbETDId):      
    prodDir = os.path.join('../', 'etdrepo')     
    firstLevelDir = firstLevelDirCalculation(dbETDId)
    secondLevelDir = secondLevelDirCalculation(dbETDId)

    etdFinalProdDir = prodDir+'/'+firstLevelDir+'/'+secondLevelDir
    etdProduction = etdFinalProdDir + '/' + str(dbETDId) + '.pdf' 
    
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
    
    #@Dennis harvestDirectory = 'UNLV_ETDs'
    harvestDirectory = 'AIT_ETDs'
    print(harvestDirectory)
    etddirs = os.listdir(harvestDirectory)
    print(etddirs)
    #etddirs = handleSuddenStop(etddirs,'metadc278485') #TODO: Change here to handle sudden production stop   #metadc53494

    print("#ETDs:", len(etddirs))
    # for i in range(1201,1211):
    for i in range(712,len(etddirs)):
        print('')
        print("Current ETD:", i)
        
        xmlFilePath = os.path.join(harvestDirectory+'/'+str(i),str(i)+'.html')
        print("xmlFilePath: ",xmlFilePath)

        # Get the pdf. Can be with any name
        # etdPath = None
        _etdPath = Path(harvestDirectory+'/'+str(i))
        for item in _etdPath.glob('*.pdf'): # Return a list
            etdPath = item
            print("etdPath:" ,etdPath)

        # Extract and insert table
            if os.path.exists(xmlFilePath):
                xmlfile = open(xmlFilePath, "r")
                soup = BeautifulSoup(xmlfile, 'lxml')
                
                # @Dennis                 
                is_exist = exists_in_etds(soup) #is_exist will be 0 or the etdid
                print('is_exist: ',is_exist)
                if is_exist:
                    etdid = is_exist
                    # return a list of empty field
                    empty_fields_list = []
                    empty_fields_list = empty_fields(soup,etdid)
                    print('empty_fields: ',empty_fields_list)
                    # update the empty field
                    if not empty_fields_list:
                        update_empty_field(soup,empty_fields_list,etdid)
                        
                    final_pdf_path = final_pdf_dir(etdid)
                    print(final_pdf_path)  
                      
                    exist_pdf_etdrepo = etdrepo_check(final_pdf_path,etdid)
                    if not exist_pdf_etdrepo:
                        moveFileToProductionRepo(etdPath,etdid)                        
                    
                    insert_haspdf_timestamp(final_pdf_path,etdid)
                    
                    
                else:   
                    etdid = insertETDs(soup) # DONE
                    # insertSubjects(soup, etdid) # DONE
                    insertPDFs(soup, etdid, etdPath, str(1001+i-1)) # Done
                    
                    #    Step 3: Shift the ETD to the production repo, rename & place file/folders based on ID
                    
                    print("etdpath",etdPath)                
                    moveFileToProductionRepo(etdPath, etdid) #Works
                    final_pdf_path = final_pdf_dir(etdid)
                    insert_haspdf_timestamp(final_pdf_path,etdid)
            
        for item in _etdPath.glob('*.html'): # Return a list
            htmlPath = item

        # Extract and insert table
            if os.path.exists(xmlFilePath):                
                
                final_html_path = final_html_dir(etdid)
                
                #    Step 3: Shift the ETD to the production repo, rename & place file/folders based on ID
                
                print("path: ",htmlPath)
                movehtml(htmlPath, etdid) #Works
                insert_metadata_timestamp(final_html_path,etdid)
                #break # Loop breaks after a run for now
            else:
                pass
            

                



if __name__ == '__main__':
    main()