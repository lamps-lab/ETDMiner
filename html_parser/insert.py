# Program to read data from JSON file and insert into SQL Server

#import mysql.connector
import json

def main():

	'''conn = mysql.connector.connect(
		host="localhost",
		user="yourusername",
		password="yourpassword",
		database="mydatabase"
	)'''

	data = {}

	f = open('data.json')
	data = json.load(f)
	f.close()

	print("print data:\n")
	print(json.dumps(data,indent=4))

	for row in data['universities']:
		print()
		title = row['Title']
		author = row['Author']
		advisor = row['Advisor']
		year = row['Year']
		abstract = row['Abstract']
		university = row['University']
		degree = row['Degree']
		uri = row['DocumentURL']
		department = row['Department']
		language = row['Language']
		
		keywords = row['Keywords']
		subjects = row['Subject']

		print(title + '\n' + author + '\n' + advisor + '\n' + str(year) + '\n' + abstract + '\n' + university 
			+ '\n' + degree + '\n' + uri + '\n' + department + '\n')
		
		# ID's are auto-generated, etdid is FK in keywords and subjects

		#conn.execute("INSERT INTO etds VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (title, author, advisor, year, abstract, university, degree, uri, department, language))
		print("Keywords: ")
		for i in keywords:
			print(i)
			#conn.execute("INSERT INTO keywords VALUES(?, ?)", (etdid, i)

		print("Subjects: ")
		for i in subjects:
			print(i)
			#conn.execute("INSERT INTO keywords VALUES(?, ?)", (etdid, i)

	#end for
#end main

if __name__ == '__main__':
	main()
