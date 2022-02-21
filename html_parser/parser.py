"""
The following Python program was written to receive dissertation as an html file, 
then parse the html dissertations using BeautifulSoup to extract metadata from articles
to store as JSON objects and then insert them into SQL database

@author: Dominik Soos
"""

# Imports
import os, argparse, glob, json
from bs4 import BeautifulSoup


# Functions to get metadata:
#	title, author, year, university, subject, advisor, team members, proq id, degree,
#	num pages, keywords, Committee member (list), Degree, Document URL, Copyright

# 	Each attribute is sliced off to get the actual information about the dataField

def getSubject(dataToParse, i):
	subject = str(dataToParse[i].text)
	subject = subject[8:len(subject):1].split(';')
	return subject

def getKeyWords(dataToParse, i):
	keywords = str(dataToParse[i].text)
	keywords = keywords[21:len(keywords):1].split(';')
	return keywords

def getTitle(dataToParse, i):
	title = str(dataToParse[i].text)
	title = title[6:len(title):1]
	return title

def getKey(dataToParse, i):
	key = str(dataToParse[i].text)
	key = key[6:len(key):1].split()
	key = key[0:4]
	return key

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
	committeeMembers = committeeMembers[17:len(committeeMembers):1].split(';')
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
	

def matching():
	x = 0;
	return x

# Main Driver
def main():
	print()
	parser = argparse.ArgumentParser(description='A foo that bars.', epilog='Please try again.')
	parser.add_argument('--path', type=str, help='Type path to folder')
	parser.add_argument('-p', type=str, help='Type path to folder')
	#parser.add_argument('-o', help='Output the JSON object')
	
	
	
	parser.parse_args()
	args = parser.parse_args()
	#print(args)
	path = args.path

	print(path)

	# get all the files from folder
	files = glob.glob(path + '*.html')

	pdfDictionary = {}
	htmlDictionary = {}
	
	# loop through each file in the folder
	for file in files:
		with open(file) as f:
			print("FileName: " + file) # filename - path
			f_name, f_ext = os.path.splitext(file)

			if(f_ext == '.html'):
				htmlFileName = os.path.basename(f_name) + f_ext
				print("HTML name: " + htmlFileName)


			content = f.read()
			soup = BeautifulSoup(content, 'html.parser')
			
			dataField = soup.find_all('div',{"class":"display_record_indexing_fieldname"}) # get all the dataFields
			dataToParse = soup.find_all('div',{"class":"display_record_indexing_row"}) # get all the data associated with the dataFields

			f.close() # close the file

			#initialize each variable before inserting data in case the next university does not have certain dataFields
			pdfFileName = pdfName = subject = keywords = title = degree = university = language = department = advisor = committeeMembers = documentURL = copyRight = f_name = f_ext = ""
			numberOfPages = publicationYear = proQuestID = 0

			for i in range(len(dataField)):
				if dataField[i].text == "Subject ":
					subject = getSubject(dataToParse, i)
				elif dataField[i].text == "Identifier / keyword ":
					keywords = getKeyWords(dataToParse, i)
				elif dataField[i].text == "Title ":
					title = getTitle(dataToParse, i)
					key = getKey(dataToParse, i)
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
			#end for

			# Bipartite matching the HTML filename with the PDF filename
			pdfFiles = glob.glob(path + '*.pdf')


			for f in pdfFiles:
				f_name, f_ext = os.path.splitext(f) # split filename into name and extension
				if(f_ext == '.pdf'):
					pdfName = os.path.basename(f_name).split(".")[0]
					print("FileExtension PDF")
					pdfFileName = pdfName + f_ext # save the actual filename with extension
					print(pdfFileName)


					pdfName = pdfName.split("_") # split pdfName into array for comparison with key
					if(key[:3] == pdfName[:3]): # found a match if first 4 words equal
						print()
						key = "_".join(key)
						pdfDictionary.update({key:pdfFileName})
						htmlDictionary.update({key:htmlFileName})

						print("HTML Dictionary: ")
						print(htmlDictionary)
						print()
						print("PDF Dictionary: ")
						print(pdfDictionary)
					#end if match
				#end if pdf
			#end for

			# Since not each university have every dataField, some entries will be null
			jsonObject = {
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
				"ProQuestID": proQuestID,
				"DocumentURL": documentURL,
				"CopyRight": copyRight
			}
			jsonObject = json.dumps(jsonObject)
			print(jsonObject)



			for i in range(4):
				print()

			#end for
		#end with
	#end for
#end main


if __name__ == '__main__':
	main()


