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

# config = {
#     'user': 'rpates',
#     'password': 'FriAug2:1316pm',
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
import requests
from urllib.parse import urljoin
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


# @Dennis check if it has license.txt / no_license.txt
def check_license_txt(cur_path):
    license_path = os.path.join(cur_path,'license.txt')
    if os.path.exists(license_path):
        return True 
    
    no_license_path = os.path.join(cur_path,'no_license.txt')
    if os.path.exists(no_license_path):
        return True   
    
    return False

# @Dennis create a new funciton to extract copyright from the uri, and go to full page, find the lience.txt, download it
def download_copyright(m_soup,cur_path):
    if not check_license_txt(cur_path) :    
        url = m_soup.find('dim:field',{'qualifier':'uri'})
        if url is not None:
            url = url.get_text()
        
        time.sleep(30)
        response = requests.get(url)
        if response.status_code == 200:
            # Parse HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            # Find the download link
            full_uri = soup.find('a', {'class': 'btn btn-outline-primary', 'href': True})
            if full_uri:
                full_uri_href = full_uri['href']
                full_uri = "https://cardinalscholar.bsu.edu/" + full_uri_href
                print("full_uri: ",full_uri)
                response = requests.get(full_uri)
                # Check if the request was successful (status code 200)    
                if response.status_code == 200:
                    # Parse HTML content
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Find the download link
                    download_link = soup.find('a', {'class': 'dont-break-out', 'href': True})
                    
                    if download_link:
                        current_download_url = download_link['href']
                        print("current_download_url: ", current_download_url)
                        
                        new_download_link = current_download_url.replace("/download", "/content")
                        print("new_download_link: ", new_download_link)
                        
                        # Get the full download URL
                        full_download_url = "https://cardinalscholar.bsu.edu/server/api/core"+ new_download_link
                        print("full_download_url: ", full_download_url)

                        # Download the content
                        download_response = requests.get(full_download_url)

                        # Check if the download request was successful
                        if download_response.status_code == 200:
                            # Save the content to a file (assuming it's a text file)
                            with open(cur_path /'license.txt', 'wb') as file:
                                file.write(download_response.content)
                            print("license.txt downloaded successfully.")
                        else:
                            print(f"Failed to download license.txt code: {download_response.status_code}")
                            with open(cur_path /'no_license.txt', 'wb') as file:
                                file.write("0")
                            
                    else:
                        print("Download link not found on the page.")
                        with open(cur_path /'no_license.txt', 'wb') as file:
                            file.write("0")
            else:
                print(f"1 Failed to retrieve content from {full_uri}. Status code: {response.status_code}")
                with open(cur_path /'no_license.txt', 'wb') as file:
                    file.write("0")
        elif response.status_code == 429:
            print(f"2 Failed to retrieve content from {url}. Status code: {response.status_code}")
            

# @Dennis create a new function extract_all_field, used to extract all field from matadata, and return a JSON.
def extract_all_field(soup,cur_path):
    # Title
    title = soup.find('dim:field',{'element':'title'})
    if title is not None:
        title = title.get_text()

    # Author @Dennis
    author_list = []
    author_elelments = soup.find_all('dim:field',{'qualifier':'author'})
    if not author_elelments:
        author = None
    else:
        for element in author_elelments:
            element_str = element.get_text()
            author_list.append(element_str)
        author = "; ".join(author_list)
    # print("author: ",author)

    # Advisor @Dennis
    advisor_list = []
    advisor_elelments = soup.find_all('dim:field',{'qualifier':'advisor'})
    if not advisor_elelments:
        advisor = None
    else:
        for element in advisor_elelments:
            element_str = element.get_text()
            advisor_list.append(element_str)
        advisor = "; ".join(advisor_list)
    # print("advisor: ",advisor)

    # Abstract
    abstract = soup.find('dim:field',{'qualifier':'abstract'})
    if abstract is not None:
        abstract = abstract.get_text()

    # Landing Page URL
    url = soup.find('dim:field',{'qualifier':'uri'})
    if url is not None:
        url = url.get_text()
    print("url: ",url)

    # Year
    date = soup.find('dim:field',{'qualifier':'issued', 'element':'date'})
    if date is not None:
        date = date.get_text()
        if date.find('-'):
            date = date.split('-')[0]

    # University
    university = soup.find('dim:field',{'qualifier':'grantor'})
    if university is not None:
        university = university.get_text()
    if university is None:
        university = "Ball State University"

    # Degree  @Dennis use element="type"
    degree = soup.find('dim:field',{'element':'type'})
    if degree is not None:
        degree = degree.get_text()
    # @Dennis use qualifier':'degree', 'element':'description'}
    # degree = soup.find('dim:field',{'qualifier':'degree', 'element':'description'})
    # if degree is not None:
    #     degree = degree.get_text()
    


     # Language
    language = soup.find('dim:field',{'qualifier':'iso', 'element':'language'})
    if language is not None:
        language = language.get_text()
    

    # Department
    department = soup.find('dim:field',{'qualifier':'sponsorship', 'element':'description'})
    if department is not None:
        department = department.get_text()

    # Discipline
    discipline = soup.find('dim:field',{'qualifier':'discipline', 'element':'degree'})
    if discipline is not None:
        discipline = discipline.get_text()
        
        
    # CopyRight link @Dennis    if has license.txt, read it to the copyright;  
    copyright = None
    license_path = cur_path / "license.txt"
    if  os.path.exists(license_path) :
        with open(license_path, "r", encoding="utf-8") as file:
            copyright = file.read()
            # print("Contents of license.txt:", copyright)
    else:
        print("The file license.txt does not exist.") 
            
    # identifier @Dennis
    pri_identifier = soup.find('dim:field',{'qualifier':'uri', 'element':'identifier'})
    if pri_identifier is not None:
        pri_identifier = pri_identifier.get_text()
    print("pri_identifier: ", pri_identifier)   
    
    second_identifier = soup.find('dim:field',{'element':'identifier'})
    if second_identifier is not None:
        second_identifier = second_identifier.get_text()
    print("second_identifier: ", second_identifier)   
    
        
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
        'pri_identifier': pri_identifier,
        'second_identifier': None,        
    }
    
    # print("data: ",data)
    return data   

# @Dennis create a new funciton to check if the record exists in the database
def exists_in_etds(soup,cur_path):
    data = extract_all_field(soup,cur_path)
    title = data.get('title')
    pri_identifier = data.get('pri_identifier')
    # second_identifier = data.get('second_identifier')
    # print(f"exists_in_etds: title:{title}, pri_identifier: {pri_identifier} ")
    
    db_connection = mysql.connector.connect(**config)
    mycursor = db_connection.cursor()

    etd_id = None
    try:
        # Check if pri_identifier exists
        query = "SELECT id FROM etds WHERE pri_identifier = %s"
        params = (pri_identifier,)
        mycursor.execute(query, params)
        result = mycursor.fetchall()

        if result:
            # pri_identifier exists
            etd_id = result[0][0]
            print("pri_identifier exists ")

        else:
            query = "SELECT id FROM etds WHERE trim(title) = trim(%s)"
            params = (title,)
            mycursor.execute(query, params)
            result = mycursor.fetchall()
            
            if result:
                # title exists
                etd_id = result[0][0]
                print("title exists ")
    finally:
        # No match found for any identifier
        mycursor.close()
        db_connection.close()    
    
    return etd_id
    
# @Dennis create a new funciton used to check if this record has any empty field
def empty_fields(soup,etdid):
    required_fields = [
        'title', 'author', 'advisor', 'year', 'university', 'URI', 'department', 'degree', 'discipline', 'language', 'abstract', 'copyright', 'pri_identifier', 'haspdf', 'timestamp_metadata','timestamp_pdf'
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
def update_empty_field(soup,empty_list,etdid,cur_path) :
    data = extract_all_field(soup,cur_path)
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
            print(f"updated the field {field}")
    mycursor.close()
    db_connection.close()     
    


def insertETDs(soup,cur_path):
   
    """
        Database insertion for ETD table
    """
    # Setup Database connection
    db_connection = mysql.connector.connect(**config)

    # Insert values to database
    mycursor = db_connection.cursor()
    data = extract_all_field(soup,cur_path)
    oads_flag = 0
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

    return etdId

def insertPDFs(soup, etdid, etdPath):
    # Get the url from XML
    urlInitials = 'https://thescholarship.ecu.edu/bitstream/handle/'
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

def final_pdf_dir(etdid):
    prodDir = os.path.join('../../', 'etdrepo')
    firstLevelDir = firstLevelDirCalculation(etdid)
    secondLevelDir = secondLevelDirCalculation(etdid)

    pdf_FinalProdDir = prodDir+'/'+firstLevelDir+'/'+secondLevelDir    
    pdf_path = pdf_FinalProdDir + '/' + str(etdid) + '.pdf'
    return pdf_path

# @Dennis create a final_html_dir(etdid) function, used to return a  final directory
def final_html_dir(etdid):
    prodDir = os.path.join('../../', 'etdrepo')
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
    prodDir = os.path.join('../../', 'etdrepo')     
    firstLevelDir = firstLevelDirCalculation(dbETDId)
    secondLevelDir = secondLevelDirCalculation(dbETDId)

    etdFinalProdDir = prodDir+'/'+firstLevelDir+'/'+secondLevelDir
    etdProduction = etdFinalProdDir + '/' + str(dbETDId) + '.pdf' 
    print(etdFinalProdDir)
    if not os.path.isdir(etdFinalProdDir):
        os.makedirs(etdFinalProdDir) 
    
    if etdPath is not None and os.path.exists(etdPath):
        copyfile(etdPath, etdProduction)


def movehtml(htmlpath, dbETDId):
    prodDir = os.path.join('../../', 'etdrepo')     
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
    # harvestDirectory = 'harvest/10342'
    # @Dennis
    harvestDirectory = 'harvest/20.500.14291'
    print(harvestDirectory)
    etddirs = os.listdir(harvestDirectory)
    #etddirs = handleSuddenStop(etddirs,'metadc278485') #TODO: Change here to handle sudden production stop   #metadc53494

    print("#ETDs:", len(etddirs))
    for etddir in etddirs:
        print('')
        print("Current ETD:", etddir)
        
        xmlFilePath = os.path.join(harvestDirectory+'/'+etddir,etddir+'.xml')
        
        # Get the pdf. Can be with any name
        etdPath = None
        _etdPath = Path(harvestDirectory+'/'+etddir)
        
        
        for item in _etdPath.glob('*.pdf'): # Return a list
            etdPath = item
            print("etdPath: ",etdPath)

        # Extract and insert table
        if os.path.exists(xmlFilePath):
            xmlfile = open(xmlFilePath, "r")
            soup = BeautifulSoup(xmlfile, 'lxml')
            # @Dennis download license.txt first
            # download_copyright(soup,_etdPath)
            is_exist = exists_in_etds(soup,_etdPath) #is_exist will be 0 or the etdid
            print('is_exist: ',is_exist)
            if is_exist:
                etdid = is_exist
                # return a list of empty field
                empty_fields_list = []
                empty_fields_list = empty_fields(soup,etdid)
                print('empty_fields: ',empty_fields_list)
                # update the empty field
                if empty_fields_list:
                    print("Prepare updating empty fields")
                    update_empty_field(soup,empty_fields_list,etdid,_etdPath)
                                
                final_pdf_path = final_pdf_dir(etdid)                
                final_html_path = final_html_dir(etdid)    
                exist_pdf_etdrepo = etdrepo_check(final_pdf_path,etdid)
                exist_html_etdrepo = etdrepo_check(final_html_path,etdid)
                # print("final_pdf_path: ", final_pdf_path)
                # print("final_html_path: ", final_html_path)
                # print("exist_pdf_etdrepo: ",exist_pdf_etdrepo)
                # print("exist_html_etdrepo: ",exist_html_etdrepo)
                if not exist_pdf_etdrepo and etdPath:
                    moveFileToProductionRepo(etdPath,etdid)                        
                if not exist_html_etdrepo:
                    movehtml(xmlFilePath, etdid)
                    
                insert_haspdf_timestamp(final_pdf_path,etdid)
                insert_metadata_timestamp(final_html_path,etdid)
                
            else:   
                etdid = insertETDs(soup,_etdPath) # DONE
                # insertSubjects(soup, etdid) # DONE
                if etdPath:
                    insertPDFs(soup, etdid, etdPath) # Done
                    moveFileToProductionRepo(etdPath, etdid) #Works
                #    Step 3: Shift the ETD to the production repo, rename & place file/folders based on ID
                
                movehtml(xmlFilePath, etdid)
                final_pdf_path = final_pdf_dir(etdid)
                insert_haspdf_timestamp(final_pdf_path,etdid)
                
                final_html_path = final_html_dir(etdid)
                insert_metadata_timestamp(final_html_path,etdid)
            
          
                
           
            

if __name__ == '__main__':
    main()