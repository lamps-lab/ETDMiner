#!/usr/bin/env pyth
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 2 14:05:43 2022

@author: muntabir
"""


import mysql.connector as mysql
import configparser
import csv
import pandas as pd

config = configparser.ConfigParser()
config.read('DB.config')


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

db_connection = mysql.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD)

print("Connected to:", db_connection.get_server_info())
mycursor = db_connection.cursor()


## Performing numerical sort
#etd_space = pd.read_csv("ETD300.csv")
#etd_space.columns = ['etd_space_id']
#etd_space.sort_values('etd_space_id', ascending=True, inplace=True, ignore_index=True)
#etd_space.to_csv("etdSpaceIDs.csv", index = None)


etd_space = pd.read_csv("etdSpaceIDs.csv")

####################################################
'''The below block of code is for 100 etd_space'''
###################################################

def tuplesTolist(tuple_text):
    etd_list = []
    for values in tuple_text:
        etd_title = list(values)
        etd_list.append(etd_title)
    
    return etd_list

def flatten(etd_record_list):
    return [item for sublist in etd_record_list for item in sublist]

db_record_list = []
for etd_idx in etd_space['etd_space_id']:
    query = f'SELECT id, title, author, year, university, degree, advisor, department FROM {etd_tablename} where id IN (%d)' % (etd_idx)
    mycursor.execute(query)
    rows = mycursor.fetchall()
    db_record = tuplesTolist(rows)
    db_record_list.append(db_record)
    
etd_record = flatten(db_record_list)

csvfile = open('etd_records_v4.csv', 'w')
writer = csv.writer(csvfile)
writer.writerow(['id', 'title', 'author', 'year', 'university', 'degree', 'advisor', 'department'])

for data in etd_record:
    writer.writerow(data)

csvfile.close()


