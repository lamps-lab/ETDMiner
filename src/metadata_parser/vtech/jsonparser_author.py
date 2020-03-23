#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 13:06:49 2020

@author: muntabirc
"""

import os, json
from nltk.tokenize import word_tokenize
import pandas as pd
import csv

# this finds our json files
path_to_json = r'C:\Users\Muntabir\Documents\Graduate School_ODU\RA\VTech_Sample\etd_metadata_vtech'
json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]

jsons_data = pd.DataFrame(columns=['author_name'])

csvfile = open("author-names_json.csv", "w")
csv_writer = csv.writer(csvfile)

for index, js in enumerate(json_files):
    with open(os.path.join(path_to_json, js)) as json_file:
        json_text = json.load(json_file)
        
        _author=[]
        author_name = json_text['Author'][0]
        jsons_data = author_name
        
        #tokenize the sentence
        word_tokens = word_tokenize(jsons_data)
        
        #normalize the sentence
        word_tokens = [word.lower() for word in word_tokens]
        
        #converting tokens to a string
        def listToString(sent_toekns):
            _string = " "
            return(_string.join(word_tokens))
                
        tokenized_string = listToString(word_tokens)
        
        _author.append([tokenized_string])

    #saving data to a .csv file
    csv_writer.writerow(_author)

csvfile.close()