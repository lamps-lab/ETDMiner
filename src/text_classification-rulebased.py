# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 13:46:29 2020

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
from sklearn.model_selection import train_test_split
import pandas as pd
from pandas import DataFrame
import numpy as np
from nameparser.config import CONSTANTS
from nameparser import HumanName
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler

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
path = r'C:\Users\Muntabir\nltk_data\corpora\cookbook\*.txt'

mypath = os.path.expanduser("~/nltk_data/corpora/cookbook")
print(mypath)

#tokenizer = RegexpTokenizer(r"^(?<=by\n)[A-Za-z\-\.\s]+$")
#author_data = (tokenizer.tokenize(tokenized_string))

files = glob.glob(path)

csvfile = open('author-names_extracted.csv', 'w')
csv_writer = csv.writer(csvfile)

#
for name in files:
        with open(name) as f:
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
            
            author_name = []
            #extracting authors from each text document
            author_data = re.findall(r'(?<=by\n)\w[^\n]*', tokenized_string)
            #print(author_data)
            author_name.append(author_data)
            
        csv_writer.writerow(author_name)

csvfile.close()

#add a column name to the extracted author names
dfList=[]
#colname=['extracted_author']
df=pd.read_csv('author-names_extracted.csv')
dfList.append(df)
concatDf=pd.concat(dfList, axis=0)
#concatDf.columns=colname
concatDf.to_csv('author-names_extracted_modified.csv', index=None)

#add a column name to both metadata author names (.xml and .json)
#for xml
dfList=[]
#colname=['metadata_author']
df=pd.read_csv('author-names_xml.csv')
dfList.append(df)
concatDf=pd.concat(dfList, axis=0)
#concatDf.columns=colname
concatDf.to_csv('author-names_xml_modified.csv', index=None)

#for json
dfList=[]
#colname=['metadata_author']
df=pd.read_csv('author-names_json.csv')
dfList.append(df)
concatDf=pd.concat(dfList, axis=0)
#concatDf.columns=colname
concatDf.to_csv('author-names_json_modified.csv', index=None)


"""
Now that we have extracted author-names from both clean data and metadata, we saved the files in .csv format.
Now, we have to write a name parser in odrer to decompose the extracted author-names from the clean data. So,
we used python package called nameparser(https://pypi.org/project/nameparser/) in order to decompose the name component 
of the extracted author-names. We called a library HumanName which allowed us to fetch the first name, middle name and last name
from the extracted author-names of clean data.

Note: the data in .csv format is in "list" format. Therefore, we had to convert the data from list format to string format and then
apply HumanName. The CONSTANT.string_format is another feature of nameparser pacakge. This allowed us to handle the name
component string in the format we want. For example: "{first} {middle} {last}"

The problem with the nameparser package that it does not support comma-separated names and list. For the author-names from metadata,
we also had to convert the author-names from the list format to string format. However, there was a comma between last name, and
first name and last name. For example: barton, thomas f. Thus, we had to split the string in order to grab the last name 
and then applied HumanName fucntion for the first and middle name.

Later, we had to clean up sapce, "]", " ' ", " . ", " \" using strip(). Finally, we stored the data in dictionary format 
for both extracted author-names and metadata author-names. Then saved it in the .csv files. 

"""
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
        data = [{'first_name1': name.first.strip("'['").strip("]"),
                    'middle_name1': name.middle,
                     'last_name1': name.last[:-1].strip("'") 
                }
         ]
        for row in data:            
            csv_writer.writerow(row)

csvfile.close()


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


df1 = pd.read_csv('extracted_author.csv')
df2 = pd.read_csv('metadata_author.csv')


#first_name_result = df1['first_name1'].isin(df2['first_name2']).value_counts()
#last_name_result = df1['last_name1'].isin(df2['last_name2'])

df3 = pd.DataFrame(columns=['first_name_status'])
df3['first_name_status'] = df1['first_name1'].isin(df2['first_name2']).replace([True, False], ['1', '0'])
df4 = pd.DataFrame(columns=['middle_name_status'])
df4['middle_name_status'] = df1['middle_name1'].isin(df2['middle_name2']).replace([True, False], ['1', '0'])
df5 = pd.DataFrame(columns=['last_name_status'])
df5['last_name_status'] = df1['last_name1'].isin(df2['last_name2']).replace([True, False], ['1', '0']) 

result = pd.concat([df1, df2, df3, df4, df5], axis = 1, sort = False)
result.to_csv("output.csv")

#evaluation

#importing the final dataset
dataset = pd.read_csv('output.csv')
X = dataset.iloc[:,1:7].values
y = dataset.iloc[:,7:].values

#encoding the categorical variables
from sklearn.preprocessing import OneHotEncoder
encoder = OneHotEncoder(handle_unknown='ignore', categorical_features = X[:,1:7])
X = encoder.fit_transform(X).toarray()



#spliting the dataset into train and test set
#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size= 0.2, random_state = 0)

#feature scaling
#sc = StandardScaler()
#X_train = sc.fit_transform(X_train)
#X_test = sc.transform(X_test)








 




        
        
        
        
        
        