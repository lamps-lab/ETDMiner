#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 21 16:33:41 2022

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


etd_space = pd.read_csv("etd_space100.csv")
year_space = pd.read_csv("year_space100.csv")
uni_space = pd.read_csv("university_space100.csv")

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
for ids in etd_space['etd_id']:
    query = 'SELECT id, title, author, year, university, degree, advisor, department FROM etds where id IN (%d)' % (ids)
    mycursor.execute(query)
    rows = mycursor.fetchall()
    db_record = tuplesTolist(rows)
    db_record_list.append(db_record)
    
etd_record = flatten(db_record_list)

csvfile = open('etdspace_record.csv', 'w')
writer = csv.writer(csvfile)
writer.writerow(['id', 'title', 'author', 'year', 'university', 'degree', 'advisor', 'department'])

for data in etd_record:
    writer.writerow(data)

csvfile.close()


####################################################
'''The below block of code is for 100 year_space'''
###################################################
    
year_record_list = []
for idx in year_space['etd_id']:
    query = 'SELECT id, title, author, year, university, degree, advisor, department FROM etds where id IN (%d)' % (idx)
    mycursor.execute(query)
    rows = mycursor.fetchall()
    year_record = tuplesTolist(rows)
    year_record_list.append(year_record)
    
etd_year_record = flatten(year_record_list)

csvfile = open('yearspace_record.csv', 'w')
writer = csv.writer(csvfile)
writer.writerow(['id', 'title', 'author', 'year', 'university', 'degree', 'advisor', 'department'])

for year in etd_year_record:
    writer.writerow(year)

csvfile.close()


####################################################
'''The below block of code is for 100 uni_space'''
###################################################
    
uni_record_list = []
for uni_idx in uni_space['etd_id']:
    query = 'SELECT id, title, author, year, university, degree, advisor, department FROM etds where id IN (%d)' % (uni_idx)
    mycursor.execute(query)
    rows = mycursor.fetchall()
    uni_record = tuplesTolist(rows)
    uni_record_list.append(uni_record)
    
etd_uni_record = flatten(uni_record_list)

csvfile = open('unispace_record.csv', 'w')
writer = csv.writer(csvfile)
writer.writerow(['id', 'title', 'author', 'year', 'university', 'degree', 'advisor', 'department'])

for uni in etd_uni_record:
    writer.writerow(uni)

csvfile.close()