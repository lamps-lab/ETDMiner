# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 00:20:22 2020

@author: Muntabir Choudhury

https://regex101.com/r/r2bMqp/2

Trial 1:
    (at the[\n| ]|from the\n|at[\n| ]|faculty of the\n)(\w.+[\n]?\w+[^,]?\w+)
Trial 2:
    (at the[\n?| ?]|faculty of the\n)(\w.+[\n]?\w+[^,]?\w+)
Trial 3:
    (at the[\n| ]|from the\n|at[\n| ]|faculty of the\n)(\w.+[\n]?\w+[^,]?\w+[ ]\w+)
Trial 4:
    (at the[\n| ]|from the\n|at[\n| ]|faculty of the[\n| ]|faculty of\n)(\w.+[\n]?\w+[^,]?\w+[ ]\w+)
Trial 5:
    (at the[\n| ]|from the\n|at[\n| ]|faculty of the\n)(\w.+[\n]?\w+[^,]?\w+[ ]?\w+) -- most likely final

Final one:
    (at the[\n| ]|from the\n|at[\n| ]|faculty of the[\n| ]|faculty of\n)(\w.+[\n]?\w+[^,]?\w+[ ]?\w+[ ]?\w+[ ]?\w+)
    
    https://regex101.com/r/r2bMqp/3
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

csvfile = open('institution_extracted.csv', 'w')
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
    institution_data = re.compile(r'(at the[\n| ]|from the\n|at[\n| ]|faculty of the[\n| ]|faculty of\n)(\w.+[\n]?\w+[^,]?\w+[ ]?\w+[ ]?\w+[ ]?\w+)')
            
    def matched(tokenized_string):
        ins = institution_data.match(tokenized_string) #giving the none values
        ins = institution_data.search(tokenized_string) #searching for the values which has a match
        if ins is None:
            return " "
        return ins.group(2) #the 2nd capturing group which is a value (i.e degree) will be returned
            
    check = matched(tokenized_string)
#    print(check)

    stopwords = ['august,', 'keith', 'scott', 'thesis', 'n.','january', 'february', 'march', 'april', 'may','in', '.', '1975', '1955', '1945', '1946',
                         'june', 'july', 'august', 'september', 'october', 'november', 'december', '1', '2', '3', '4', '5', '6', '7',
                         '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', 'n',
                         '25', '26', '27', '28', '29', '30', '31', '1970', '1965', '1950', '1964', 's.b.,', '5.m.,', 'mech.', 'e.,', 'author','redacted',
                         'spring', 'signature', 'partial', 'fulfillment', 'his/her', 'initial', 'appointment', 'holes', 'composite', 'laminates',
                         'by', 'doron', 'shalev', 'moment', 'solution', 'linda', 'e', 'the']
    key = check.split() #spliting the strings
#    print(key)
    resultwords = [word for word in key if word not in stopwords] #iterating through words in each row and checking the stopwords that needs to be removed
    result = ' '.join(resultwords).rstrip('of').strip() #joining the words with a space after removing the stopwords

    institution = []
    institution.append([result])
    #print(institution)
    csv_writer.writerow(institution)

csvfile.close()

dfList=[]
colname=['extracted_university']
df = pd.read_csv("institution_extracted.csv", header = None)
dfList.append(df)
concatDf = pd.concat(dfList, axis =0)
concatDf.columns=colname
concatDf.to_csv("extracted_institution.csv",index = None)

df1 = pd.read_csv("extracted_institution.csv")
df2 = pd.read_csv("metadata_ins.csv")

df3 = pd.DataFrame(columns=['ins_match'])
df3['ins_match'] = df1['extracted_university'].eq(df2['university']).replace([True, False], [1,0])
result = pd.concat([df1, df2, df3], axis = 1, sort = False)
result.to_csv("ins_output.csv")

df4 = pd.read_csv("ins_output.csv")
count = df4['ins_match'].value_counts()
print(count)

