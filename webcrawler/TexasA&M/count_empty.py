import json
import os
import mysql.connector
from bs4 import BeautifulSoup
from shutil import copyfile
import xml.etree.ElementTree as ET
import urllib.request
import urllib.response
import urllib.parse
import re
import requests

#@Dennis
# config = {
#     'user': 'uddin',
#     'password': 'TueJul271:56:04PM',
#     'host': 'hawking.cs.odu.edu',
#     'database': 'pates_etds'
# }

config = {
    'user': 'Dennis',
    'password': '1234',
    'host': 'localhost',  # or '127.0.0.1'
    'database': 'testdb' 
}





def count_empty_fields(column_name):
    db_connection = mysql.connector.connect(**config)
    mycursor = db_connection.cursor(dictionary=True)

    # Assuming 'etds' is the table name
    query = f"SELECT COUNT(*) as count FROM etds WHERE {column_name} IS NULL AND university = 'Texas A&M University'"
    mycursor.execute(query)
    result = mycursor.fetchone()

    mycursor.close()
    db_connection.close()

    return result['count']

def check_empty_fields():
    columns = ['title', 'author', 'advisor', 'year', 'university', 'URI', 'department', 'degree', 'discipline',
               'language', 'abstract', 'copyright', 'pri_identifier', 'second_identifier', 'haspdf',
               'timestamp_metadata', 'timestamp_pdf']

    for column in columns:
        empty_count = count_empty_fields(column)
        print(f"Empty {column} count: {empty_count}")
        
# count this college's all record        
def count_total():        
    
    db_connection = mysql.connector.connect(**config)
    mycursor = db_connection.cursor(dictionary=True)
    query = f"SELECT COUNT(*) as count FROM etds WHERE university = 'Texas A&M University' "
    mycursor.execute(query)
    result = mycursor.fetchone()
    print("Total count: ", result['count'])

    mycursor.close()
    db_connection.close()
    
def count_has_no_pdf():
    db_connection = mysql.connector.connect(**config)
    mycursor = db_connection.cursor(dictionary=True)
    query = f"SELECT COUNT(*) as count FROM etds WHERE haspdf = 0 AND university = 'Texas A&M University'"
    mycursor.execute(query)
    result = mycursor.fetchone()
    print("Has no pdf: ", result['count'])

    mycursor.close()
    db_connection.close()

# Example usage
check_empty_fields()
count_has_no_pdf()
count_total()

