#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 13:06:49 2020

@author: muntabirc
"""

import os, json
from nltk.tokenize import word_tokenize
import csv
import glob
import pandas as pd
import re

# this finds our json files
path_to_json = r'C:\Users\Muntabir\Documents\Graduate School_ODU\RA\VTech_Sample\etd_metadata_vtech'
numbers = re.compile(r'(\d+)')
def numericalSort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts


#json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
json_files = sorted(glob.glob("*.json"), key=numericalSort)
#jsons_data = pd.DataFrame(columns=['author_name'])

csvfile = open("program_json.csv", "w")
csv_writer = csv.writer(csvfile)

for index, js in enumerate(json_files):
    with open(os.path.join(path_to_json, js)) as json_file:
        json_text = json.load(json_file)
        
        _program=[]
        program_data = json_text['Subject'][0]
        jsons_data = program_data
        
        #tokenize the sentence
        word_tokens = word_tokenize(jsons_data)
        
        #normalize the sentence
        word_tokens = [word.lower() for word in word_tokens]
        
        #converting tokens to a string
        def listToString(sent_toekns):
            _string = " "
            return(_string.join(word_tokens))
                
        tokenized_string = listToString(word_tokens)
        
        
        _program.append([tokenized_string])
        print(_program)

    #saving data to a .csv file
    csv_writer.writerow(_program)

csvfile.close()
#
#dfList=[]
##colname=['metadata_author']
#df=pd.read_csv('year_json.csv')
#dfList.append(df)
#concatDf=pd.concat(dfList, axis=1)
##concatDf.columns=colname
#concatDf.to_csv('year_json_modified.csv', index=None)