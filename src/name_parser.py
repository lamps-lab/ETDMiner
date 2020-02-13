# -*- coding: utf-8 -*-
"""
Created on Sun Feb  9 15:47:53 2020

@author: Muntabir Hasan Choudhury
"""

import csv
import pandas as pd
from nameparser.config import CONSTANTS
from nameparser import HumanName

csvfile = open('extracted_author.csv', 'w')        
fieldnames = ('first_name1', 'middle_name1', 'last_name1')
csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
csv_writer.writeheader()
#read the extracted author-names from the clean data and convert data from list to string
with open("author-names_extracted_modified.csv", 'r', encoding="utf-8") as f:
    for lines in f:
        list_string = lines
         #converting author list in string
        def listExtractedString(list_string):
            str1 = ""
            return(str1.join(list_string))
         
         #saved the result of the author list to string convertion
        authorListtoString = listExtractedString(list_string)
        #print(authorListtoString)
        CONSTANTS.string_format = "{first} {middle} {last} ({suffix})"
        name = HumanName(authorListtoString)           
        data = [
                {'first_name1': name.first.strip("'['").strip("]"),
                  'middle_name1': name.middle, 
                  'last_name1': name.last[:-1].strip("'")
                  } 
         ]
        for row in data:            
            csv_writer.writerow(row)

csvfile.close()

dfList=[]
df=pd.read_csv('extracted_author.csv')
dfList.append(df)
concatDf=pd.concat(dfList, axis=0)
concatDf.to_csv('extracted_author_updated.csv', index=True)





csvfile = open('metadata_author.csv', 'w')
#fieldnames = ('Floor', 'Use', 'Square Footage', 'Price', 'RoomID', 'Capacity')
fieldnames = ('first_name2', 'middle_name2', 'last_name2')
csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
csv_writer.writeheader()

with open("author-names_metadata.csv", 'r', encoding="utf-8") as f:
    for each_line in f:
        string_list = each_line
        #converting author list in string
        def listMetadataString(string_list):
            str2 = ""
            return(str2.join(string_list))
        
        #saved the result of the author list to string convertion
        authortoString = listMetadataString(string_list)
        author_fname_mname = authortoString.split(",")[-1]
        apply_nameparser = HumanName(author_fname_mname)
        data1 = [
                {'first_name2': apply_nameparser.first.strip(']("\")').strip("'"),
                    'middle_name2': apply_nameparser.last.strip(".").strip('"]"').strip("'"),
                  'last_name2':  authortoString.split(",")[0].strip('"["').strip("'")
                }
        ]
        for rows in data1:
            csv_writer.writerow(rows)                            

csvfile.close()

dfList=[]
df=pd.read_csv('metadata_author.csv')
dfList.append(df)
concatDf=pd.concat(dfList, axis=0)
concatDf.to_csv('metadata_author_updated.csv', index=True)