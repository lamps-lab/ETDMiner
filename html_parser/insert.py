"""
Program to read data from JSON file and insert into SQL DB
and to generate folder structure to store ETDs as both HTML and PDF

@author: Dominik Soos
"""

# Imports
import os,sys, argparse, glob, json
import pymysql.cursors
import config
import shutil

# Function to create structure folder and moving the matching HTML and PDF files
def movingFiles(path, etdid, dictionary):
	# get the names from dictionary
	pdfName, htmlName = list(dictionary.items())[0]
	upperFolder = int(etdid / 10000)
	lowerFolder = etdid % 10000

	# Padding upperFolder
	if upperFolder < 10:
		upperFolder = str('00' + str(upperFolder))
	elif upperFolder < 100:
		upperFolder = str('0' + str(upperFolder))

	# Padding lowerFolder
	lowerFolder = etdid % 10000
	if lowerFolder < 10:
		lowerFolder = str('000' + str(lowerFolder))
	elif lowerFolder < 100:
		lowerFolder = str('00' + str(lowerFolder))
	elif lowerFolder < 1000:
		lowerFolder = str('0' + str(lowerFolder))


	# at root
	currentPath = os.path.abspath(os.getcwd()) + '/'
	upperPath = currentPath + upperFolder + '/'

	# create upperFolder if it doesn't exist
	if not os.path.exists(upperPath):
		os.mkdir(upperPath)

	os.chdir(upperPath)
	# inside upperFolder

	# create lowerFolder if it doesn't exist
	lowerPath = upperPath + str(lowerFolder) +'/'
	if not os.path.exists(lowerPath):
		os.mkdir(lowerPath)

	os.chdir(lowerPath)
	# inside lowerFolder
	
	# create source and target paths for each
	targetPath = lowerPath
	pdfSourcePath = os.path.join(path, str(pdfName))
	htmlSourcePath = os.path.join(path, str(htmlName))
	pdfDestinationPath = os.path.join(targetPath, str(pdfName))
	htmlDestinationPath = os.path.join(targetPath, str(htmlName))

	# Copy matched HTML & PDF
	shutil.copyfile(pdfSourcePath, pdfDestinationPath)
	shutil.copyfile(htmlSourcePath, htmlDestinationPath)

	# Rename both HTML & PDF based on their ETDID in DB
	newPDF = targetPath + str(etdid) + ".pdf"
	newHTML = targetPath + str(etdid) + ".html"
	os.rename(pdfDestinationPath, newPDF)
	os.rename(htmlDestinationPath, newHTML)

	os.chdir(currentPath)
	# back to root

# Function to insert metadata into database
def insertMetadata(data):
	# init
	numberOfDocuments = 0
	fail = 0

	# create root dir if it doesn't exist
	root = os.getcwd() + "/root"
	if not os.path.exists(root):
		os.makedirs(root)

	# get inside root
	os.chdir('root')

	# get metadata from JSON file
	for row in data['ETDs']:
		numberOfDocuments += 1
		path = row['path']
		title = row['Title']
		author = row['Author']
		advisor = row['Advisor']
		year = row['Year']
		discipline = row['Discipline']
		abstract = row['Abstract']
		university = row['University']
		degree = row['Degree']
		uri = row['DocumentURL']
		department = row['Department']
		language = row['Language']
		
		keywords = row['Keywords']
		subjects = row['Subject']

		dictionary = row['dictionary']

		# connect to SQL database
		connection = pymysql.connect(
			host = config.host,
			user = config.user,
			password = config.password,
			database = config.database,
			cursorclass=pymysql.cursors.DictCursor)

		### Insertion to DB ###
		etdid = 0
		with connection:
			with connection.cursor() as cursor:
				
				# IDs are auto-generated
				sql = "INSERT INTO `etds` (`title`, `author`, `advisor`, `year`, `abstract`, `university`, `degree`, `URI`, `department`,`discipline`, `language`, `schooltype`) VALUES(%s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s)"
				values = (title, author, advisor, year, abstract, university, degree, uri, department, discipline, language, 'HBCU')
				
				try:
					cursor.execute(sql, values)
					etdid = cursor.lastrowid
				except:
					print(dictionary)

				# etdid is FK in keywords and subjects
				for i in keywords:
					cursor.execute("INSERT INTO `keywords` (`etdid`, `keyword`) VALUES(%s, %s)", (etdid, i))

				for i in subjects:
					cursor.execute("INSERT INTO `subjects` (`etdid`, `subject`) VALUES(%s, %s)", (etdid, i))

			connection.commit()

		### File Matching ###
		if bool(dictionary):
			movingFiles(path, etdid, dictionary)

			# real time stats
			percent = round((1 - fail/numberOfDocuments) * 100, 2)
			if numberOfDocuments % 100 == 0:
				print(percent,"\n" ,university)
			
		# count failure if files aren't matched up	
		else:
			fail += 1

	#end for ETDs
	print("Completed all files")
	print("     ------- STATS -------")
	print("Total number of documents: ", numberOfDocuments)
	print("Total dictionary failures: ", fail)
	percent = str(round((1 - fail / numberOfDocuments) * 100, 2))
	print("Percent: ", percent + "%")


def main():
	# init
	data = {}
	f = open('data.json')
	data = json.load(f)
	f.close()

	insertMetadata(data)
		
#end main

if __name__ == '__main__':
	main()
