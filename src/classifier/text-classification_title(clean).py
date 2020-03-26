# -*- coding: utf-8 -*-
"""
Created on Sun Mar 22 17:50:42 2020

@author: Muntabir Choudhury

Trial 1: 
    ((.*\n){5}|(.*\n){4}|(.*\n){3}|(.*\n){2}|(.*\n){1})(?=by)
   https://regex101.com/r/ExHyYu/2
"""

import os, os.path
import glob
import re
import csv
import nltk.data
import nltk
from nltk.tokenize import sent_tokenize
import pandas as pd


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
#print(mypath)


numbers = re.compile(r'(\d+)')
def numericalSort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts


files = sorted(glob.glob(path), key=numericalSort)

csvfile = open('title_extracted.csv', 'w')
csv_writer = csv.writer(csvfile)


for name in files:

    directory = os.path.split(name)
    document = nltk.data.load(directory[1])

    #tokenize the sentence
    sent_tokens = sent_tokenize(document)
    #normalize the sentence
    sent_tokens = [sent.lower() for sent in sent_tokens]
            
    #converting tokens to a string
    def listToString(sent_toekns):
        _string = " "
        return(_string.join(sent_tokens))
                
    tokenized_string = listToString(sent_tokens)

            #extracting degree from each text document
    title_data = re.compile(r'((.*\n){5}|(.*\n){4}|(.*\n){3}|(.*\n){2}|(.*\n){1})(?=by)')
            
    def matched(tokenized_string):
        title = title_data.match(tokenized_string) #giving the none values
        title = title_data.search(tokenized_string) #searching for the values which has a match
        if title is None:
            return " "
        return title.group(1) #the 4th capturing group which is a value (i.e degree) will be returned
            
    check = matched(tokenized_string)
    
    """
    Since we have multiple lines as a title a '\n' was added after each line. Therefore, we have to remove \n after each line and 
    save the string in a single list. In the below block of code, the 'key' operation is spliting the strings first and 
    then in the result 'strip' takes care of 
    removing '\n' at the end of the line.
    """
    key = check.split() #spliting the strings

    result = ' '.join(key).strip() #removing 'space', '\n' etc.
            
    _title = []
    _title.append([result])
    #print(_title)
         
    csv_writer.writerow(_title)

csvfile.close()

dfList=[]
colname=['extracted_title']
df = pd.read_csv("title_extracted.csv", encoding = 'latin1', header = None)
dfList.append(df)
concatDf = pd.concat(dfList, axis =0)
concatDf.columns=colname
concatDf.to_csv("extracted_title.csv",index = None, encoding = 'utf-8') #appended column and saved as dataframe

df1 = pd.read_csv("extracted_title.csv")
df2 = pd.read_csv("metadata_title.csv")

df3 = pd.DataFrame(columns=['title_match'])
df3['title_match'] = df1['extracted_title'].eq(df2['title']).replace([True, False], [1,0])
result = pd.concat([df1, df2, df3], axis = 1, sort = False)
result.to_csv("title_output.csv")

df4 = pd.read_csv("title_output.csv")
count = df4['title_match'].value_counts()
print(count)