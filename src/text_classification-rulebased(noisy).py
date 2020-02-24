# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 13:46:29 2020

@author: Muntabir Hasan Choudhury
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

#printing the textfile which exist in the custom nltk corpus
path = r'C:\Users\Muntabir\nltk_data\corpora\cookbook\noisy_data\*.txt'

mypath = os.path.expanduser("~/nltk_data/corpora/cookbook/noisy_data/")
print(mypath)

#tokenizer = RegexpTokenizer(r"^(?<=by\n)[A-Za-z\-\.\s]+$")
#author_data = (tokenizer.tokenize(tokenized_string))

numbers = re.compile(r'(\d+)')
def numericalSort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts


files = sorted(glob.glob(path), key=numericalSort)

csvfile = open('author-names_extracted.csv', 'w')
csv_writer = csv.writer(csvfile)


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
            author_name.append(author_data)
            
        csv_writer.writerow(author_name)

csvfile.close()

#add a column name to the extracted author names
dfList=[]
df=pd.read_csv('author-names_extracted.csv')
dfList.append(df)
concatDf=pd.concat(dfList, axis=0)
concatDf.to_csv('author-names_extracted_modified.csv', index=None)


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

#applied nameparser on extracted author names from clean data and saved the result in extracted_author.csv file
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
  
# applied nameparser on the metadata (ground-truth) and saved the result in metadata_author.csv file
csvfile = open('metadata_author.csv', 'w')
fieldnames = ('first_name2', 'middle_name2', 'last_name2')
csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
csv_writer.writeheader()
  
with open("metadata_author-names.csv", 'r', encoding="utf-8") as f:
      for each_line in f:
          string_list = each_line
          #converting author list in string
          def listMetadataString(string_list):
              str2 = ""
              return(str2.join(string_list))
          
          #saved the result of the author list to string convertion
          authortoString = listMetadataString(string_list)
          last_name2 =  authortoString.split(",")[0].strip('"["').strip("'").strip()
          author_fname_mname = authortoString.split(",")[-1]
          CONSTANTS.string_format = "{first} {middle} {last} ({suffix})"
          apply_nameparser = HumanName(author_fname_mname)
          data1 = [
                  
                  {'first_name2': apply_nameparser.first.strip(']("\")').strip("'"),
                      'middle_name2': apply_nameparser.last.strip(".").strip('"]"').strip("'"),
                        'last_name2':  last_name2
                  }
          ]
          for rows in data1:
              csv_writer.writerow(rows)                            
 
csvfile.close()
 
 
# #evaluation
df1 = pd.read_csv('extracted_author.csv')
df2 = pd.read_csv('metadata_author.csv')
 
df3 = pd.DataFrame(columns=['first_name_status'])
df3['first_name_status'] = df1['first_name1'].eq(df2['first_name2']).replace([True, False], ['1', '0'])
df4 = pd.DataFrame(columns=['middle_name_status'])
df4['middle_name_status'] = df1['middle_name1'].eq(df2['middle_name2']).replace([True, False], ['1', '0'])
df5 = pd.DataFrame(columns=['last_name_status'])
df5['last_name_status'] = df1['last_name1'].eq(df2['last_name2']).replace([True, False], ['1', '0'])
result = pd.concat([df1, df2, df3, df4, df5], axis = 1, sort = False)
#result.to_csv("output.csv")
 
df6 = pd.read_csv("output.csv")
matched = df6['first_name_status'].eq(df6['last_name_status']).replace([True, False], ['1', '0'])
df6['matched'] = matched
#df6.to_csv("output_result.csv")

df7 = pd.read_csv("output_result.csv")
count = df7['matched'].value_counts()
print(count)