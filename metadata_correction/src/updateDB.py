#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-

#title         	:autometa.py
#description  	:This code iterates through each row in the original ETD table to look for missing values.
# 				 If a missing value(s) is found, it would check the metadata miner autoMeta to obtain the missing values. 
# 				 If missing values were found, the original ETD table will be updated with these missing data while the original row is backed up in the new shadow table. 
# 				 The orig ETD table will have a new version number incremented by 1.
#author			:Himarsha R. Jayanetti 
#date         	:Wednesday, April 06, 2022
#===================================================================================================


import mysql.connector as mysql
import configparser

config = configparser.ConfigParser()
config.read('autometa.config')


#enter your server IP address/domain name
HOST = config['SERVER_CONFIG']['HOST']
# this is the user you create
USER = config['SERVER_CONFIG']['USER']
# user password
PASSWORD = config['SERVER_CONFIG']['PASSWORD']
# database name, if you want just to connect to MySQL server, leave it empty
DATABASE = config['DATABASE_CONFIG']['DATABASE']

#Update the original ETD tabel name and the Shadow table name here
etd_tablename = config['DATABASE_CONFIG']['ETD_TABLE']
shadow_tablename = config['DATABASE_CONFIG']['SHADOW_TABLE']

db_connection = mysql.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD)
print("Connected to:", db_connection.get_server_info())
mycursor = db_connection.cursor()


#To obtain etd path from ID (this is not used).
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
	with open("CRF_output/metadata.csv","r") as f:
		autoMeta_rows = f.readlines()
		#print(autoMeta_rows)
	autoMeta_rows.pop(0)
	for row in autoMeta_rows:
		row = row.split(",")
		#print(row[0],str(id))
		if row[0] == str(id):
			#ETD found
			#print("FOUND")
			ETD_found = True
			for field in field_list:
				idx =  [i for i,x in enumerate(index_map) if x == field]
				missing_val[field] = row[idx[0]].strip("\n")
			break
		else:
			#ETD not found
			#print(f"ETD ID {id} is not found in autometa data\n")
			ETD_found = False
			#pass

	#print(ETD_found)
	return ETD_found, missing_val

def update_etdTable(id,autoMeta_values_dic,current_version):
	new_version = current_version + 1
	index_map = ["id","title","author","advisor","year","","university","degree","","program"]
	for key in autoMeta_values_dic:
		value = autoMeta_values_dic[key]
		if key == "program":
			key = "department"
			value = autoMeta_values_dic["program"]
		sql_cmd3 = f"UPDATE {etd_tablename} SET {key} = '{value}' WHERE id = {id};"
		mycursor.execute(sql_cmd3) 
		db_connection.commit()

	sql_cmd4 = f"UPDATE {etd_tablename} SET version = {new_version} WHERE id = {id};"
	mycursor.execute(sql_cmd4) 
	db_connection.commit()

	

def update_shadowTable(id,current_row):	
	#print(current_row)
	for item in current_row:
		if item == None:
			item = 'NULL'
		new_current_row.append(item)
	if new_current_row:
		current_row = new_current_row	
	original_method = config['METADATA_UPDATE_CONFIG']['ORIG_METHOD']
	update_method = config['METADATA_UPDATE_CONFIG']['UPDATE_METHOD']
	new_columns = [original_method,update_method]
	current_row.extend(new_columns)
	insert_data = tuple(current_row)
	sql_cmd2 = f"insert into {shadow_tablename} (etdid,title,author,advisor,year,abstract,university,degree,URI,department,discipline,language,schooltype,version,original_method,update_method) values {insert_data};"
	mycursor.execute(sql_cmd2) 
	db_connection.commit()


if __name__ == "__main__":
	limit = config['DATABASE_CONFIG']['ETD_TABLE_LIMIT']
	#print(limit)
	if limit == "all":
		sql_cmd1 = f"SELECT * FROM {etd_tablename};" 
	else:
		sql_cmd1 = f"SELECT * FROM {etd_tablename} limit {limit};"
	mycursor.execute(sql_cmd1) 
	rows = mycursor.fetchall() 
	#print("\nUpdates info\n\nid,fields,values")
	print("Iterating through the database rows looking for missing values ...")
	for row in rows:
		index_map = ["id","title","author","advisor","year","","university","degree","","program"]
		autoMeta_fields = [1,2,3,4,6,7,9]
		current_row = list(row)
		new_current_row = []
		id = row[0]
		print(id)
		current_version = row[13]
		has_missingVAL = not all(current_row)
		#print( "ID, HAS MISSING VALUE",id, has_missingVAL)
		if has_missingVAL:
			#Has missing values in the row
			index_list = [i for i,d in enumerate(current_row) if d==None or d=="NULL"]
			#print(index_list,autoMeta_fields)
			#check if atleast one element in the index_list is available in the index_map
			is_autoMeta_field = not set(index_list).isdisjoint(autoMeta_fields)
			#print("ID, is_autoMeta_field",id, is_autoMeta_field)
			if is_autoMeta_field:
				#The row has NULL values in fields that we can find in autoMeta
				common = list(set(index_list).intersection(autoMeta_fields))
				field_list = []
				for i in common:
					field = index_map[i]
					field_list.append(field)
				ETD_found, autoMeta_values_dic = check_autometa(id,field_list)
				#print(ETD_found,autoMeta_values_dic)
				#Updating the ETD table
				if ETD_found:
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
	print("Done.")