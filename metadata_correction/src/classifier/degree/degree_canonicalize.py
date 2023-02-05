import pandas as pd
import re
import mysql.connector as mysql
import configparser
from datetime import date
config = configparser.ConfigParser()
config.read('updateDB.config')


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
# It takes a CSV file as input which has two columns(ETDID, DEGREE)
dataset = pd.read_csv('filename') 
etds = pd.DataFrame(dataset)

degree_list =[]
degree_dictionary = pd.read_csv('degree_dictionary.csv')

for index, row in etds.iterrows():
    etd_id = row[0]
    try:
      degree = (row[1]).upper()
      degree = re.sub(r'[^\w\s]','',degree)
      # print(degree)
      for id, row2 in degree_dictionary.iterrows():
        acronym = row2[0].upper()
        acronym = re.sub(r'[^\w\s]','',acronym)
        full_name = row2[1]
        if(degree==acronym):
          key = "degree"
          etd_tablename = "etds_test2"
          # sql_cmd4 = f"UPDATE etds_test2 SET advisor = {advisor_val} WHERE id = {etd_id};"
          sql_cmd4 = f"UPDATE {etd_tablename} SET {key} = '{full_name}' WHERE id = {etd_id};"
          mycursor = db_connection.cursor(buffered=True)
          mycursor.execute(sql_cmd4) 
          db_connection.commit()

          print("UPDATED")
    except:
      pass
