"""
Created on Sun 10 March, 2022
@author: Himarsha Jayanetti
"""

import mysql.connector as mysql
from nameparser import HumanName
from datetime import date

# enter your server IP address/domain name
HOST = "hawking.cs.odu.edu" # or "domain.com"
# database name, if you want just to connect to MySQL server, leave it empty
DATABASE = "pates_etds"
# this is the user you create
USER = "himarsha"
# user password
PASSWORD = "TueDec212:17:34PM"
# connect to MySQL server
db_connection = mysql.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD)
print("Connected to:", db_connection.get_server_info())
mycursor = db_connection.cursor()
# enter your code here!

etd_tablename = "etds_test2"
shadow_tabename = ""

def check_year(year):
	#is it a digit?
	#four digits
	#from 1900 to 2022
	todays_date = date.today()
	validated = False
	if year is None:
		validated = True
		return validated
	if year == "None":
		validated = True
		return validated
	if year.isdigit():
		if int(year) >=1700 and int(year) <=todays_date.year:
			validated = True
	#print(validated)
	return validated

def check_name(name):
	#author & advisor
	validated = False
	if name is None:
		validated = True
		return validated
	if name == "None":
		validated = True
		return validated
	if name.isdigit():
		return validated
	name = HumanName(name)
	if name.middle:
		#validated = name.first + " " + name.middle + " " + name.last 
		validated = True
	else:
		#validated = name.first + " " + name.last 
		validated = True
	return validated

if __name__ == "__main__":	
	# sql_cmd1 = f"SELECT id,year FROM {etd_tablename};" #Remove limit when running on the whole database*****
	# mycursor.execute(sql_cmd1) 
	# rows = mycursor.fetchall() 
	# #print(rows)
	# for row in rows:
	# 	id = row[0]
	# 	year = row[1]
	# 	year_validation = check_year(year)
	# 	#print(year,year_validation)
	# 	if year_validation:
	# 		pass
	# 	else:
	# 		print(id,year)
	# 		pass
	sql_cmd2 = f"SELECT id,author FROM {etd_tablename};" #Remove limit when running on the whole database*****
	mycursor.execute(sql_cmd2) 
	rows = mycursor.fetchall() 
	#print(rows)
	print("Author Validation Failed:\n")
	for row in rows:
		id = row[0]
		author = row[1]
		author_validation = check_name(author)
		# print(author,author_validation)	
		# print(advisor,advisor_validation)
		if author_validation:
			pass
		else:
			print(id,author)
			pass
	sql_cmd3 = f"SELECT id,advisor FROM {etd_tablename};" #Remove limit when running on the whole database*****
	mycursor.execute(sql_cmd3) 
	rows = mycursor.fetchall() 
	#print(rows)	
	print("Advisor Validation Failed:\n")
	for row in rows:
		id = row[0]
		advisor = row[1]
		advisor_validation = check_name(advisor)
		if advisor_validation:
			pass
		else:
			print(id,advisor)
			pass