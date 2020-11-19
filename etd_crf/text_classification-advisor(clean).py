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
#print(varbool)

#printing the textfile which exist in the custom nltk corpus

path = r'C:\Users\jhima\nltk_data\*.txt'
mypath = os.path.expanduser("~/nltk_data")

#tokenizer = RegexpTokenizer(r"^(?<=by\n)[A-Za-z\-\.\s]+$")
#author_data = (tokenizer.tokenize(tokenized_string)


numbers = re.compile(r'(\d+)')
def numericalSort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts


files = sorted(glob.glob(path), key=numericalSort)

csvfile = open('advisor_extracted.csv', 'w')
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
    advisor_data = re.compile(r'(certified by\n?|approved:\n?|approved by:\n?)(\w[^,?].+)')
            
    def matched(tokenized_string):
        advisor = advisor_data.match(tokenized_string) #giving the none values
        advisor = advisor_data.search(tokenized_string) #searching for the values which has a match
        if advisor is None:
            return " "
        return advisor.group(2) #the 4th capturing group which is a value (i.e degree) will be returned
            
    check = matched(tokenized_string)
    #print(check)

    stopwords = ['accepted', 'by', 'chairman', 'a', 'co-chairman', '(co-chair)', 'chair', 'thesis', 'supervisor', 
                 'supervisor.', 'supervisor,', 'head,', 'department', 'of', 'city', 'and', 'regional', 'planning']
    key = check.split() #spliting the strings
    #print(key)
    resultwords = [word for word in key if word not in stopwords] #iterating through words in each row and checking the stopwords that needs to be removed
    result = ' '.join(resultwords).strip(',') #joining the words with a space after removing the stopwords
    #print(result)

    _advisor = []
    _advisor.append([result])
    #print(_advisor)
    csv_writer.writerow(_advisor)

csvfile.close()

#add a column name to the extracted author names
dfList=[]
#colname=['extracted_advisor']
df = pd.read_csv("advisor_extracted.csv", encoding = 'latin')
dfList.append(df)
concatDf = pd.concat(dfList, axis =0)
#concatDf.columns=colname
concatDf.to_csv("extracted_advisor.csv",index = None, encoding = 'latin')


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
csvfile = open('extracted_advisor-names.csv', 'w')        
fieldnames = ('first_name1', 'middle_name1', 'last_name1')
csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
csv_writer.writeheader()
#read the extracted author-names from the clean data and convert data from list to string
with open("extracted_advisor.csv", 'r', encoding="utf-8") as f:
      for lines in f:
          list_string = lines
          #converting author list in string
          def listExtractedString(list_string):
              str1 = ""
              return(str1.join(list_string))
          
          #saved the result of the author list to string convertion
          authorListtoString = listExtractedString(list_string)
          #print(authorListtoString)
          #CONSTANTS.string_format = "{first} {middle} {last} ({suffix})"
          name = HumanName(authorListtoString)
          first = name.as_dict()["first"]
          middle = name.as_dict()["middle"]
          last = name.as_dict()["last"]
          #print(last.strip("']"))
          data = [{'first_name1': first.strip("'['").strip("]"),
                      'middle_name1': middle,
                      'last_name1': last.strip("']") 
                  }
          ]
          #print(data)
          for row in data:
              #print(row)
              csv_writer.writerow(row)
 
csvfile.close()
 
# applied nameparser on the metadata (ground-truth) and saved the result in metadata_author.csv file
csvfile = open('metadata_advisor-names.csv', 'w')
fieldnames = ('first_name2', 'middle_name2', 'last_name2')
csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
csv_writer.writeheader()
 
with open("advisor_metadata.csv", 'r', encoding="utf-8") as f:
      next(f) #Skiping the header row 'author' in the metadata file
      for each_line in f:
          string_list = each_line
          #converting author list in string
          def listMetadataString(string_list):
              str2 = ""
              return(str2.join(string_list))         
          #saved the result of the author list to string convertion
          authortoString = listMetadataString(string_list)
          name = HumanName(authortoString)
          first = name.as_dict()["first"]
          middle = name.as_dict()["middle"]
          last = name.as_dict()["last"]
          #print(last)
          data1 = [{'first_name2': first,
                      'middle_name2': middle,
                      'last_name2': last
                  }
          ]
          #print(data1) 
          for rows in data1:
              #print(rows)
              csv_writer.writerow(rows)                            

csvfile.close()

#Evaluation
#reading two csv files
df1 = pd.read_csv('extracted_advisor-names.csv', encoding = "latin")
#print(df1)
df2 = pd.read_csv('metadata_advisor-names.csv', encoding = "latin")
#print(df2)
#
df3 = pd.DataFrame(columns=['first_name_status'])
df3['first_name_status'] = df1['first_name1'].eq(df2['first_name2']).replace([True, False], ['1', '0'])
df4 = pd.DataFrame(columns=['middle_name_status'])
df4['middle_name_status'] = df1['middle_name1'].eq(df2['middle_name2']).replace([True, False], ['1', '0'])
df5 = pd.DataFrame(columns=['last_name_status'])
df5['last_name_status'] = df1['last_name1'].eq(df2['last_name2']).replace([True, False], ['1', '0'])

result = pd.concat([df1, df2, df3, df4, df5], axis = 1, sort = False)
result.to_csv("output.csv", index = None, encoding = 'utf-8')

df6 = pd.read_csv("output.csv")
fn_status = df6['first_name_status']
ln_status = df6['last_name_status']
def status_match(fn_status, ln_status):
    if fn_status == 1 and ln_status == 1:
        status = 1
    else:
        status = 0
    return status
#matched = df6['first_name_status'].eq(df6['last_name_status']).replace([True, False], ['1', '0'])
#df6['matched'] = matched

match_status = []

for f,l in zip(fn_status, ln_status):
    #print(f,l)
    status = status_match(f, l)
    status = str(status)
    match_status.append(status)

df7 = pd.DataFrame(match_status, columns=['matched'])
df7.to_csv("output_result.csv")
#print(df7)
result = pd.concat([df6,df7], axis = 1, sort = False)
result.to_csv("advisor_output.csv")
df8 = pd.read_csv("advisor_output.csv")
count = df8['matched'].value_counts()
print(count)

#applied nameparser on the visual inpect metadata (ground-truth) and saved the result in metadata_advisor_names-inspect.csv file
csvfile = open('metadata_advisor_names-inspect.csv', 'w')
fieldnames = ('first_name2', 'middle_name2', 'last_name2')
csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
csv_writer.writeheader()
 
with open("metadata_advisor-inspect.csv", 'r', encoding="utf-8") as f:
      next(f)
      for each_line in f:
          string_list = each_line
          #converting author list in string
          def listMetadataString(string_list):
              str2 = ""
              return(str2.join(string_list))
         
          #saved the result of the author list to string convertion
          authortoString = listMetadataString(string_list)
          name = HumanName(authortoString)
          first = name.as_dict()["first"]
          middle = name.as_dict()["middle"]
          last = name.as_dict()["last"]
          #print(last)
          data2 = [{'first_name2': first,
                      'middle_name2': middle,
                      'last_name2': last
                  }
                   
          ]
          #print(data2) 
          for rows in data2:
              #print(rows)
              csv_writer.writerow(rows)                            

csvfile.close()

df8 = pd.read_csv("metadata_advisor_names-inspect.csv", encoding = 'latin')

df9 = pd.DataFrame(columns=['first_name_status'])
df9['first_name_status'] = df1['first_name1'].eq(df8['first_name2']).replace([True, False], ['1', '0'])
df10 = pd.DataFrame(columns=['middle_name_status'])
df10['middle_name_status'] = df1['middle_name1'].eq(df8['middle_name2']).replace([True, False], ['1', '0'])
df11 = pd.DataFrame(columns=['last_name_status'])
df11['last_name_status'] = df1['last_name1'].eq(df8['last_name2']).replace([True, False], ['1', '0'])

result = pd.concat([df1, df8, df9, df10, df11], axis = 1, sort = False)
result.to_csv("output-inspect.csv", index = None, encoding = 'utf-8' )

df12 = pd.read_csv("output-inspect.csv")

fn_status = df12['first_name_status']
ln_status = df12['last_name_status']
def status_match(fn_status, ln_status):
    if fn_status == 1 and ln_status == 1:
        status = 1
    else:
        status = 0
    return status
#matched = df6['first_name_status'].eq(df6['last_name_status']).replace([True, False], ['1', '0'])
#df6['matched'] = matched

match_status = []

for f,l in zip(fn_status, ln_status):
    #print(f,l)
    status = status_match(f, l)
    status = str(status)
    match_status.append(status)

df13 = pd.DataFrame(match_status, columns=['matched'])
df13.to_csv("output_result-inspect.csv")
#print(df7)
result = pd.concat([df12,df13], axis = 1, sort = False)
result.to_csv("advisor_output_inspect.csv")
df13 = pd.read_csv("advisor_output_inspect.csv")
count = df13['matched'].value_counts()
print(count)

# matched = df12['first_name_status'].eq(df12['middle_name_status']).eq(df12['last_name_status']).eq(df12['first_name_status']).eq(df12['last_name_status']).replace([True, False], ['1', '0'])
# df12['matched'] = matched
# #df12.to_csv("matched_ouput.csv")

# df13 = pd.read_csv("matched_ouput.csv")
# count = df13['matched'].value_counts()
# print(count)