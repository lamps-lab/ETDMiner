# -*- coding: utf-8 -*-
"""Created on Thu Mar 12 22:55:09 2020

@author: Muntabir Choudhury

Regular Expression:
    (in?)(\n\w.+) - VTech
((department of)( ?)(\w.+)) - MIT

Most likely final one:
(department of ?|^in\n)(\w+ ?.+.)

Fine tuned Regexp:
    (department of ?)(\w+ ?\w+[^,]\w+)
    
    (department of ?)(\w+ ?\w+[^,]\w+ ?[and?\n| ?]\w+ ?\w+)
    
    (department of ?)(\w+ ?\w+[^,]\w+[^,]\w+)
    
    (department(s)? of |in\n)(\w+[ ]?\w+[^,]?\w+[^,]?\w+[^,]?\w+[ ]?\w+) -- final one
    
    (department of ?|in\n)(\w+ ?\w+[^,]\w+[^,]\w+[^,]\w+ ?\w+)
    
    https://regex101.com/r/voXFW6/1
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

csvfile = open('program_extracted.csv', 'w')
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
    program_data = re.compile(r'(department(s)? of |in\n)(\w+[ ]?\w+[^,]?\w+[^,]?\w+[^,]?\w+[ ]?\w+)')
            
    def matched(tokenized_string):
        program = program_data.match(tokenized_string) #giving the none values
        program = program_data.search(tokenized_string) #searching for the values which has a match
        if program is None:
            return " "
        return program.group(3).strip('\n').strip() #the 4th capturing group which is a value (i.e degree) will be returned
            
    check = matched(tokenized_string)
    #print(check)

    stopwords = ['certified', 'by' 'fibers', 'by', 'thesis', 'approved:','january', 'february', 'march', 'april', 'may', 'by:', 
                         'june', 'july', 'august', 'september', 'october', 'november', 'december', '1', '2', '3', '4', '5', '6', '7',
                         '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', 
                         '25', '26', '27', '28', '29', '30', '31', 'approved', 'supervisor', 'at', 'the', 'massachusetts', 'institute']
    key = check.split() #spliting the strings
    #print(key)
    resultwords = [word for word in key if word not in stopwords] #iterating through words in each row and checking the stopwords that needs to be removed
    result = ' '.join(resultwords).rstrip(',').strip() #joining the words with a space after removing the stopwords

    program = []
    program.append([result])
    #print(program)
    csv_writer.writerow(program)

csvfile.close()

dfList=[]
colname=['extracted_academic-program']
df = pd.read_csv("program_extracted.csv", header = None)
dfList.append(df)
concatDf = pd.concat(dfList, axis =0)
concatDf.columns=colname
concatDf.to_csv("extracted_program.csv",index = None)

df1 = pd.read_csv("extracted_program.csv")
df2 = pd.read_csv("metadata_program.csv")
df3 = pd.read_csv("metadata_program_visual-inspect.csv")

#comparison between extracted program field and ground truth from xml and json files
df4 = pd.DataFrame(columns=['program_match'])
df4['program_match'] = df1['extracted_academic-program'].eq(df2['academic-program']).replace([True, False], ['1', '0'])

#comparison between extracted program field and visual-inspected ground truth
df5 = pd.DataFrame(columns=['visual-inspected-match'])
df5['visual-inspected-match'] = df1['extracted_academic-program'].eq(df3['academic-program_visual-inspect']).replace([True, False], ['1', '0'])

result = pd.concat([df1, df2, df3, df4, df5], axis = 1, sort = False)
result.to_csv("academic-program_output.csv")

df6 = pd.read_csv("academic-program_output.csv")
count1 = df5['visual-inspected-match'].value_counts()
count2 = df4['program_match'].value_counts()
print(count1)
print(count2)