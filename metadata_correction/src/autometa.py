#!/usr/bin/env python3
"""
@author: himarsha
@email: hjaya002@odu.edu
@create date: 2022-04-06 09:47:00
@modify date:
@desc:

This code iterates through each row in the original ETD table to look for missing values.
If a missing value(s) is found, it would check the metadata miner autoMeta to obtain the 
missing values. If missing values were found, the original ETD table will be updated with
these missing data while the original row is backed up in the new shadow table. The orig
ETD table will have a new version number incremented by 1.

"""

import mysql.connector as mysql

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

def insert_into(field,value):
	pass

#use this later
def get_etd_path(id):
		level1 = int(id/10000)
		level2 = row[0]%10000
		level1 = str(level1).zfill(3)
		path = str(level1)+"/"+str(level2)
		return path

def check_autometa(id,field_list):
	#autometa
	index_map = ["id","title","author","advisor","year","university","degree","program"]
	missing_val = {}
	with open("test_data_input.csv","r") as f:
		autoMeta_rows = f.readlines()
	for row in autoMeta_rows:
		row = row.split(",")
		#print(row)
		if row[0] == str(id):
			#ETD found
			#print(row)
			for field in field_list:
				idx =  [i for i,x in enumerate(index_map) if x == field]
				#print(idx[0])
				missing_val[field] = row[idx[0]].strip("\n")
			#print(missing_val)

		else:
			#ETD not found
			#print(f"ETD ID {id} is not found in autometa data\n")
			pass
	#print(missing_val)
	return missing_val

def update_etdTable(id,autoMeta_values_dic,current_version):
	new_version = current_version + 1
	index_map = ["id","title","author","advisor","year","","university","degree","","program"]
	for key in autoMeta_values_dic:
		#print(key)
		#print(autoMeta_values_dic[key])
		value = autoMeta_values_dic[key]
		if key == "program":
			key = "department"
			value = autoMeta_values_dic["program"]
		sql_cmd3 = f"UPDATE etds_test2 SET {key} = '{value}' WHERE id = {id};"
		#print(sql_cmd3)
		mycursor.execute(sql_cmd3) 
		db_connection.commit()

	sql_cmd4 = f"UPDATE etds_test2 SET version = {new_version} WHERE id = {id};"
	mycursor.execute(sql_cmd4) 
	db_connection.commit()
	#print(autoMeta_values_dic.keys())

	

def update_shadowTable(id,current_row):	
	#print(current_row)
	for item in current_row:
		if item == None:
			item = 'NULL'
			#item = "'{}'".format(str(item).replace("'", "''"))
		new_current_row.append(item)
	if new_current_row:
		current_row = new_current_row	
	#print(current_row)	
	#mycursor_shadow = db_connection.cursor()
	#etdid = id
	#timestamp is expected to auto update - check******
	original_method = "library"
	update_method = "autometa"
	#print(original_method,update_method)
	new_columns = [original_method,update_method]
	current_row.extend(new_columns)
	#print(current_row)
	insert_data = tuple(current_row)
	#print(insert_data)
	sql_cmd2 = f"insert into shadow_test2 (etdid,title,author,advisor,year,abstract,university,degree,URI,department,discipline,language,schooltype,version,original_method,update_method) values {insert_data};"
	#print(sql_cmd2)
	mycursor.execute(sql_cmd2) 
	db_connection.commit()


if __name__ == "__main__":
	sql_cmd1 = f"SELECT * FROM {etd_tablename} limit 3;" #Remove limit when running on the whole database*****
	mycursor.execute(sql_cmd1) 
	rows = mycursor.fetchall() 
	print("\nUpdates info\n\nid,fields,values")
	for row in rows:
		index_map = ["id","title","author","advisor","year","","university","degree","","program"]
		autoMeta_fields = [1,2,3,4,6,7,9]
		current_row = list(row)
		new_current_row = []
		id = row[0]
		current_version = row[13]
		has_missingVAL = not all(current_row)
		if has_missingVAL:
			#Has missing values in the row
			index_list = [i for i,d in enumerate(current_row) if d==None]
			#check if atleast one element in the index_list is available in the index_map
			is_autoMeta_field = not set(index_list).isdisjoint(autoMeta_fields)
			if is_autoMeta_field:
				#The row has NULL values in fields that we can find in autoMeta
				common = list(set(index_list).intersection(autoMeta_fields))
				field_list = []
				for i in common:
					field = index_map[i]
					field_list.append(field)
				autoMeta_values_dic = check_autometa(id,field_list)
				#print(id,autoMeta_values_dic)
				#Updating the ETD table
				update_etdTable(id,autoMeta_values_dic,current_version)
				#Updating the Shadow table
				update_shadowTable(id,current_row)
			else:
				#The row has NULL values but they are not the columns that we can find in autoMeta
				autoMeta_values_dic = {}
				#print("Has missing values but not in autoMeta")
				pass
		fields = f"{list(autoMeta_values_dic.keys())}"
		values = f"{list(autoMeta_values_dic.values())}"
		print(id,fields,values)
		#break


