#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 13:06:49 2020

@author: Muntabir Hasan Choudhury
"""

import os, json
from nltk.tokenize import word_tokenize
import csv
import glob
import pandas as pd
import re
from nameparser.config import CONSTANTS
from nameparser import HumanName

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

csvfile = open("advisor_json.csv", "w")
csv_writer = csv.writer(csvfile)

for index, js in enumerate(json_files):
    with open(os.path.join(path_to_json, js)) as json_file:
        def advisor_exist(json_data):
            json_text = json.load(json_file)
            try:
                if json_text['Advisor']:
                    return  json_text['Advisor'][0]
            except KeyError:
                return ''
        
        data = advisor_exist(json_file)
        
        #normalize the sentence
        word_tokens = [word.lower() for word in data]
        
        #converting word tokens to a string
        def listToString(sent_toekns):
            _string = " ".strip()
            return(_string.join(word_tokens))
                
        tokenized_string = listToString(word_tokens)
        key = tokenized_string.split()
        
        """
        The advisors names in the json files are comma separated and also the name apperead in the first is actually a last name.
        In order to keep names consistent with the MIT parsed advisor names, we have to split each word and remove all the commas after last name (i.e. appeared as a first name)
        Then, concatanate and rearrange the name in first, middle, and last name order
        """
        last_name = key[0:1] #fetch the all first words and these names are last names 
        fm_name = key[1:]  #fetch the remaining names and these names are the  first and middle names
        
        last_words = [word for word in key if word in last_name] #this holds all the last names with commas but in the list format
        fm_words = [word for word in key if word in fm_name] # this hold all the first and middle names
        lastwords_result = ' '.join(last_words).rstrip(',').strip() #now we are converting last words to a string and removed all the commas
        
        lastwordsToList = []
        lastwordsToList.append(lastwords_result) #then append all the last names in a list format

        #concatanate the first and middle name with the last names in a list
        for i in lastwordsToList:
            fm_words.append(i)
        
        advisor_names = fm_words #saved the list of advisor name in a first, middle, last naming order (i.e. f., richard, bloss)
        
        #In order to keep consitent with the MIT parsed data we had to convert list to string (i.e. f. richard bloss)
        def listToString(name):
            _string = " "
            return(_string.join(advisor_names))
            
        check = listToString(advisor_names)
            
        _advisor = []
        _advisor.append([check])
        #print(_advisor)

    #saving data to a .csv file
    csv_writer.writerow(_advisor)

csvfile.close()
