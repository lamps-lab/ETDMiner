#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 16 00:17:30 2020

@author: Muntabir Choudhury
"""

import csv
import pandas as pd
from nameparser import HumanName


csvfile = open('pr_author.csv', 'w')        
fieldnames = ('first_name1', 'middle_name1', 'last_name1')
csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
csv_writer.writeheader()
#read the extracted author-names from the clean data and convert data from list to string
with open("2-prauthor.csv", 'r', encoding="utf-8") as f:
     for lines in f:
         list_string = lines
          #converting author list in string
         def listExtractedString(list_string):
             str1 = ""
             return(str1.join(list_string))
          
          #saved the result of the author list to string convertion
         authorListtoString = listExtractedString(list_string)
         name = HumanName(authorListtoString)
         data = [{'first_name1': name.first.strip(),
                     'middle_name1': name.middle,
                      'last_name1': name.last
                 }
          ]
         for row in data:
             #print(row)
             csv_writer.writerow(row)
 
csvfile.close()

csvfile = open('gt_author.csv', 'w')
fieldnames = ('first_name2', 'middle_name2', 'last_name2')
csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
csv_writer.writeheader()
 
with open("author_gt.csv", 'r', encoding="latin") as f:
      for lines in f:
          last =  lines.strip().split(",")[0].strip('"')
          first_middle = lines.split(",")[1].strip().strip('"')
          name = HumanName(first_middle)
          first = name.first
          middle = name.last
          data = [{'first_name2': first,
                     'middle_name2': middle,
                      'last_name2': last 
                 }
          ]
          for row in data:
              csv_writer.writerow(row)
 
csvfile.close()

#reading two csv files
df1 = pd.read_csv('pr_author.csv')
df2 = pd.read_csv('gt_author.csv')

df3 = pd.DataFrame(columns=['first_name_status'])
df3['first_name_status'] = df1['first_name1'].eq(df2['first_name2']).replace([True, False], ['1', '0'])
df4 = pd.DataFrame(columns=['middle_name_status'])
df4['middle_name_status'] = df1['middle_name1'].eq(df2['middle_name2']).replace([True, False], ['1', '0'])
df5 = pd.DataFrame(columns=['last_name_status'])
df5['last_name_status'] = df1['last_name1'].eq(df2['last_name2']).replace([True, False], ['1', '0'])

result = pd.concat([df1, df2, df3, df4, df5], axis = 1, sort = False)
result.to_csv("author_output.csv")

df6 = pd.read_csv("author_output.csv")
fn_status = df6['first_name_status']
ln_status = df6['last_name_status']
def status_match(fn_status, ln_status):
    if fn_status == 1 and ln_status == 1:
        status = 1
    else:
        status = 0
    return status


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
result.to_csv("author_crf-match.csv", index = None)
df8 = pd.read_csv("author_crf-match.csv")
count = df8['matched'].value_counts()
print(count)
