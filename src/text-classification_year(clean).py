# -*- coding: utf-8 -*-aaaa
"""
Created on Mon Feb 24 11:42:46 2020

@author: Muntabir
"""

#import libraries
import os, os.path
import glob
import re
import csv
import nltk.data
import nltk
from nltk.tokenize import sent_tokenize
import pandas as pd
from nameparser.config import CONSTANTS
from nameparser import HumanName

#create nltk_data directory in the root
mypath = os.path.expanduser("~/nltk_data")

#check to see if the folder exist or not
if not os.path.exists(mypath):
    os.mkdir(mypath)
    print('Folder Created!')

else:
    print("Folder exists")
    
#check to see the validity of the existance of the folder
varbool = mypath in nltk.data.path
#print(varbool)

#printing the textfile which exist in the custom nltk corpus
path = r'C:\Users\Muntabir\nltk_data\corpora\cookbook\clean_data\*.txt'

mypath = os.path.expanduser("~/nltk_data/corpora/cookbook/clean_data")
print(mypath)

#tokenizer = RegexpTokenizer(r"^(?<=by\n)[A-Za-z\-\.\s]+$")
#author_data = (tokenizer.tokenize(tokenized_string)


numbers = re.compile(r'(\d+)')
def numericalSort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts

files = sorted(glob.glob(path), key=numericalSort)

csvfile = open('year_extracted.csv', 'w')
csv_writer = csv.writer(csvfile)

for name in files:
        with open(name) as f:
            directory = os.path.split(name)
            document = nltk.data.load(directory[1])
            
            year_result = re.compile(
                    r"(Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|"
                    "Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|"
                    "Dec(ember)?)(,?)(\s\d{4})")
            
#            year = year_result.search(document)
#            print(year)
#            if year:
#                print(year.group(14))
            
            def matched(document):                   
                    year = year_result.match(document)
                    year = year_result.search(document)
                    if year is None:
                        return '0'
                    return year.group(14)
                                   
            check = matched(document)
            key = check.strip()
            year_data = []
            year_data.append(key)               
            csv_writer.writerow([year_data])
                
csvfile.close()

dfList=[]
colname=['extracted_year']
df = pd.read_csv("year_extracted.csv", header = None)
dfList.append(df)
concatDf = pd.concat(dfList, axis =0)
concatDf.columns=colname
concatDf.to_csv("extracted_year.csv",index = None)
#print(concatDf)

df1 = pd.read_csv("extracted_year.csv")
    

df2 = pd.read_csv("metadata_year.csv")

df3 = pd.DataFrame(columns=['year_status'])
df3['year_status'] = df1['extracted_year'].eq(df2['year']).replace([True, False], ['1', '0'])

result = pd.concat([df1, df2, df3], axis = 1, sort = False)
result.to_csv("year_output.csv")

df4 = pd.read_csv("year_output.csv")
count = df4['year_status'].value_counts()
print(count)

          
"""
Year Extraction:

Year which starts with a month without comma separated including space: Example -- June 1930            
(^(?<month>)\w+\s[0-9]{4})
Year which starts with a month with comma separated and including space: Example -- June, 1930
(^(?<month>)\w+,\s[0-9]{4})

if we combine the both regular expression:
^(?<month>)\w+\s[0-9]{4}|(^(?<fmonth>)\w+,\s[0-9]{4}$)   

[A-Za-z]\w+ (\d{4})
([A-Za-z]\w+,\s(\d{4}))
[A-Za-z]\w+ (\d{4})|([A-Za-z]\w+,\s(\d{4}))    


^\w+,?\s+[0-9]{4}(?!\d)   
"""            
            
            
            
            
            
            
            
            
            
            