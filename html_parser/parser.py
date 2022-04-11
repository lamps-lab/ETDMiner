"""
The following Python program was written to receive a path to the dissertations, 
parse the html dissertations using BeautifulSoup to extract metadata
store data in .json as output

@author: Dominik Soos
"""

# Imports
import os, argparse, glob, json
from bs4 import BeautifulSoup

# Longest Common Subsequence Function
def lcs(X , Y):
    # find the length of the strings
	m = len(X)
	n = len(Y)

    # declaring the array for storing the dp values
	L = [[None]*(n+1) for i in range(m+1)]
	"""Following steps build L[m+1][n+1] in bottom up fashion
    Note: L[i][j] contains length of LCS of X[0..i-1]
    and Y[0..j-1]"""
	for i in range(m+1):
		for j in range(n+1):
			if i == 0 or j == 0 :
				L[i][j] = 0
			elif X[i-1] == Y[j-1]:
				L[i][j] = L[i-1][j-1]+1
			else:
				L[i][j] = max(L[i-1][j] , L[i][j-1])
    # L[m][n] contains the length of LCS of X[0..n-1] & Y[0..m-1]
	return L[m][n]
#end of function lcs


def bipartiteMatching(path, originalHTML, og):
	dictionary = {}
	pdfFiles = glob.glob(path + '/*.pdf')
	for pdf in pdfFiles:
		# init
		pdfFileName = ""

		# clean up htmlfilename
		htmlFileName = os.path.basename(og)
		htmlFileName = htmlFileName.replace(".", "")
		htmlFileName = htmlFileName.replace("_", "")
		htmlFileName = htmlFileName.split()
		#print("html: ", htmlFileName)
		f_name, f_ext = os.path.splitext(pdf) # split filename into name and extension


		# This is where thre problem could be
		pdfName = os.path.basename(f_name).split(".")[0]

		# save the actual filename with extension
		pdfFileName = pdfName + f_ext

		# clean up any extra dots
		pdfName = pdfName.replace(".", "")
		pdfName = pdfName.split("_") # split pdfName into array for comparison with key
		pdfName = list(filter(None, pdfName)) # remove empty spaces from array

		# HTML and PDF has the same length array
		htmlFileName = htmlFileName[:len(pdfName)]

		# join the string array for comparison
		htmlFileName = ''.join(htmlFileName)
		pdfName = ''.join(pdfName)
		pdfName = pdfName.replace("_", "")
		
		# get the longest common subsequence 
		longest = lcs(pdfName, htmlFileName)
		# threshold of 90%
		percent = len(pdfName) * 0.9

		# if its a 90%+ similarity then its a match
		# update dictionary
		if longest > percent:
			dictionary.update({pdfFileName:originalHTML})
			percentMatch = round((1 - longest/len(pdfName)) * 100, 2)
			return dictionary
	#end for pdfFiles

def metadataExtraction(path, f, dictionary):
	originalHTML = pdfFileName = pdfName = subject = abstract = keywords = title = degree = university = language = department = advisor = committeeMembers = documentURL = copyRight = f_name = f_ext = ""
	numberOfPages = publicationYear = proQuestID = 0
	content = f.read()
	f.close()
	soup = BeautifulSoup(content, 'html.parser')

	# get all the data associated with the dataFields
	# based on ProQuest HTML files.
	dataField = soup.find_all('div',{"class":"display_record_indexing_row"})
	dataToParse = soup.find_all('div',{"class":"display_record_indexing_data"})

	# some ETD's might not have an abstract
	abstract = soup.find('div',{"class": "abstract truncatedAbstract"})
	try:
		abstract = str(abstract.text)
	except:
		abstract = ""

	# each dataField have the same name in each ETD
	for i in range(len(dataField)):
		if dataField[i].text == "Subject" or dataToParse[i].text == "Subject":
			subject = str(dataToParse[i].text).split(';')
		elif "Classification" in dataField[i].text:
			discipline = str(dataToParse[i].text).split(':')
			for i in range(len(discipline)-1):
				d = discipline[i]
				discipline[i] = d[:-4]
			discipline.pop(0)
			discipline = ', '.join(discipline)
		elif "Identifier / keyword " in dataField[i].text:
			keywords = str(dataToParse[i].text).split(';')
		elif "Title" in dataField[i].text:
			title = str(dataToParse[i].text)
		elif "Author" in dataField[i].text:
			author = str(dataToParse[i].text)
		elif "Number of pages " in dataField[i].text:
			numberOfPages = str(dataToParse[i].text)
		elif "Publication year " in dataField[i].text:
			publicationYear = str(dataToParse[i].text)
		elif "Degree " in dataField[i].text:
			degree = str(dataToParse[i].text)
		elif "University/institution " in dataField[i].text:
			university = str(dataToParse[i].text)
		elif "Department " in dataField[i].text:
			department = str(dataToParse[i].text)
		elif "Advisor " in dataField[i].text:
			advisor = str(dataToParse[i].text)
		elif "Committee member " in dataField[i].text:
			committeeMembers = str(dataToParse[i].text).split(';')
		elif "Language " in dataField[i].text:
			language = str(dataToParse[i].text)
		elif "ProQuest document ID " in dataField[i].text:
			proQuestID = str(dataToParse[i].text)
		elif "Document URL " in dataField[i].text:
			documentURL = str(dataToParse[i].text)
		elif "Copyright " in dataField[i].text:
			copyRight = str(dataToParse[i].text)
	# end for

	# create JSON object based on metadata including the path
	jsonObject = {
		"path": path + '/',
		"dictionary": dictionary,
		"Title": title,
		"Author": author,
		"Advisor": advisor,
		"Year": publicationYear,
		"Discipline": discipline,
		"Abstract": abstract,
		"University": university,
		"Degree": degree,
		"Subject": subject,
		"Keywords": keywords,
		"NumberOfPages": numberOfPages,
		"Department": department,
		"Language": language,
		"CommitteeMembers": committeeMembers,
		"ProQuestID": proQuestID,
		"DocumentURL": documentURL,
		"CopyRight": copyRight
	}
	return jsonObject

# Main Driver
def main():
	parser = argparse.ArgumentParser(description='This program is to extract metadata from html files', epilog='Please try again.')
	parser.add_argument('--path', type=str, help='Type path to source directory')
	
	parser.parse_args()
	args = parser.parse_args()
	path = args.path

	# for stats
	numberOfDocuments = 0
	fail = 0
	success = 0
	notfound = ""

	result = "{\n\"ETDs\": [\n"

	pdfDictionary = {}
	htmlDictionary = {}

	rootdir = path

	# walk through each directory in folder structure to check for html files
	for subdir, dirs, files in os.walk(rootdir):
		for file in files:
			if file.endswith('.html'):
				file = os.path.join(rootdir,subdir,file)
				path = os.path.join(rootdir, subdir)
				dictionary = {}
				with open (file) as f:
					#initialize each variable before inserting data in case the next university does not have certain dataFields
					
					numberOfDocuments += 1

					# get base and extension name of each file
					f_name, f_ext = os.path.splitext(file)
					og = os.path.basename(f_name)
					f_name = os.path.basename(f_name.replace("_", "")) # clean up underscores
				
					# save original html filename
					originalHTML = og + f_ext

					### Matching HTML files with PDF files ###
					dictionary = bipartiteMatching(path, originalHTML, og)

					### Metadata Extraction ###
					jsonObject = metadataExtraction(path, f, dictionary)

					# check for matching failures
					if not dictionary:
						fail += 1
						notfound = notfound + originalHTML + "\n\n"
					else:
						# get some real time stats
						if numberOfDocuments % 100 == 0:
							percent = round((1 - fail/numberOfDocuments) * 100, 2)
							print(percent,"%\n",jsonObject['University'])

					result = result + str(json.dumps(jsonObject)) + ",\n" # add the JSON object into the result followed by a new line and a comma
				continue
			#end if html
		#end for files in dir
	#end for directories

	# write notfound filename into txt file
	notfoundFiles = open("notfound.txt", "w")
	notfoundFiles.write(notfound)
	notfoundFiles.close()

	# remove last two chars and add ] at the end to match json syntax
	result = result[:-2] + "\n]\n}" 
	with open ("data.json", "w") as outfile:
		outfile.write(result)


	print("     ------- STATS -------")
	print("Total number of documents: ", numberOfDocuments)
	print("Total dictionary failures: ", fail)
	percent = round((1 - fail / numberOfDocuments) * 100, 2)
	print("bipartiteMatching is", percent,"% efficient")
#end main


if __name__ == '__main__':
	main()


