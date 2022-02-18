"""
The following Python program was written to receive dissertation as an html file, 
then parse the html dissertations using BeautifulSoup to extract metadata from articles
to store as JSON objects and then insert them into SQL database

@author: Dominik Soos
"""

# Imports
from bs4 import BeautifulSoup
import glob
import json

# Functions to get metadata:
#	title, author, year, university, subject, advisor, team members, proq id, degree,
#	num pages, keywords, Committee member (list), Degree, Document URL, Copyright

# 	Each attribute is sliced off to get the actual information about the dataField

def getSubject(dataToParse, i):
	subject = str(dataToParse[i].text)
	subject = subject[8:len(subject):1]
	subject = subject.split(';')
	return subject

def getKeyWords(dataToParse, i):
	keywords = str(dataToParse[i].text)
	keywords = keywords[21:len(keywords):1]
	keywords = keywords.split(';')
	return keywords

def getTitle(dataToParse, i):
	title = str(dataToParse[i].text)
	title = title[6:len(title):1]
	return title

def getPDFName(dataToParse, i):
	pdfName = str(dataToParse[i].text)
	pdfName = pdfName[6:len(pdfName):1]
	pdfName = pdfName.split()
	pdfName = "_".join(pdfName)
	return pdfName

def getAuthor(dataToParse, i):
	author = str(dataToParse[i].text)
	author = author[7:len(author):1]
	return author

def getNumberOfPages(dataToParse, i):
	numberOfPages = str(dataToParse[i].text)
	numberOfPages = numberOfPages[16:len(numberOfPages):1]
	numberOfPages = int(numberOfPages)
	return numberOfPages

def getPublicationYear(dataToParse, i):
	publicationYear = str(dataToParse[i].text)
	publicationYear = publicationYear[17:len(publicationYear):1]
	publicationYear = int(publicationYear)
	return publicationYear

def getAdvisor(dataToParse, i):
	advisor = str(dataToParse[i].text)
	advisor = advisor[8:len(advisor):1]
	return advisor

def getCommitteeMembers(dataToParse, i):
	committeeMembers = str(dataToParse[i].text)
	committeeMembers = committeeMembers[17:len(committeeMembers):1]
	committeeMembers = committeeMembers.split(';')
	return committeeMembers

def getUniversity(dataToParse, i):
	university = str(dataToParse[i].text)
	university = university[23:len(university):1]
	return university

def getDepartment(dataToParse, i):
	department = str(dataToParse[i].text)
	department = department[11:len(department):1]
	return department

def getLanguage(dataToParse, i):
	language = str(dataToParse[i].text)
	language = language[9:len(language):1]
	return language

def getDegree(dataToParse, i):
	degree = str(dataToParse[i].text)
	degree = degree[7:len(degree):1]
	return degree

def getProQuestID(dataToParse, i):
	proQuestID = str(dataToParse[i].text)
	proQuestID = proQuestID[22:len(proQuestID):1]
	proQuestID = int(proQuestID)
	return proQuestID

def getDocumentURL(dataToParse, i):
	documentURL = str(dataToParse[i].text)
	documentURL = documentURL[13:len(documentURL):1]
	return documentURL

def getCopyRight(dataToParse, i):
	copyRight = str(dataToParse[i].text)
	copyRight = copyRight[10:len(copyRight):1]
	return copyRight
	

# Main Driver
def main():
	# get all the files from folder
	files = glob.glob('books/*.html')

	# loop through each file in the folder
	for file in files:
		with open(file) as f:
			content = f.read()
			soup = BeautifulSoup(content, 'html.parser')
			
			dataField = soup.find_all('div',{"class":"display_record_indexing_fieldname"}) # get all the dataFields
			dataToParse = soup.find_all('div',{"class":"display_record_indexing_row"}) # get all the data associated with the dataFields

			f.close() # close the file

			#initialize each variable before inserting data in case the next university does not have certain dataFields
			pdfName = subject = keywords = title = degree = university = language = department = advisor = committeeMembers = documentURL = copyRight = ""
			numberOfPages = publicationYear = proQuestID = 0

			for i in range(len(dataField)):

				if dataField[i].text == "Subject ":
					subject = getSubject(dataToParse, i)
				elif dataField[i].text == "Identifier / keyword ":
					keywords = getKeyWords(dataToParse, i)
				elif dataField[i].text == "Title ":
					title = getTitle(dataToParse, i)
					pdfName = getPDFName(dataToParse, i)
				elif dataField[i].text == "Author ":
					author = getAuthor(dataToParse, i)
				elif dataField[i].text == "Number of pages ":
					numberOfPages = getNumberOfPages(dataToParse, i)
				elif dataField[i].text == "Publication year ":
					publicationYear = getPublicationYear(dataToParse, i)
				elif dataField[i].text == "Degree ":
					degree = getDegree(dataToParse, i)
				elif dataField[i].text == "University/institution ":
					university = getUniversity(dataToParse, i)
				elif dataField[i].text == "Department ":
					department = getDepartment(dataToParse, i)
				elif dataField[i].text == "Advisor ":
					advisor = getAdvisor(dataToParse, i)
				elif dataField[i].text == "Committee member ":
					committeeMembers = getCommitteeMembers(dataToParse, i)
				elif dataField[i].text == "Language ":
					language = getLanguage(dataToParse, i)
				elif dataField[i].text == "ProQuest document ID ":
					proQuestID = getProQuestID(dataToParse, i)
				elif dataField[i].text == "Document URL ":
					documentURL = getDocumentURL(dataToParse, i)
				elif dataField[i].text == "Copyright ":
					copyRight = getCopyRight(dataToParse, i)

			# Since not each university have every dataField, some entries will be null
			x = {
				"title": title,
				"author": author,
				"subject": subject,
				"keywords": keywords,
				"numberOfPages": numberOfPages,
				"publicationYear": publicationYear,
				"university": university,
				"department": department,
				"language": language,
				"advisor": advisor,
				"committeeMembers": committeeMembers,
				"degree": degree,
				"PDFName": pdfName,
				"ProQuestID": proQuestID,
				"DocumentURL": documentURL,
				"CopyRight": copyRight
			}
			jsonObject = json.dumps(x)
			print(jsonObject)


#end main


if __name__ == '__main__':
	main()


