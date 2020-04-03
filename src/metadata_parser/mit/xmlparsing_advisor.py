# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 03:51:15 2020

@author: Muntabir Choudhury 
"""
from nltk.tokenize import sent_tokenize
import re
import glob
import csv
import pandas as pd
import xml.etree.ElementTree as ET

path = r"C:\Users\Muntabir\Documents\Graduate School_ODU\RA\MIT_Sample\etd_metadata_xml"

#file sorting
numbers = re.compile(r'(\d+)')
def numericalSort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts

files = sorted(glob.glob("*.xml"), key=numericalSort)
author = ''
prefix_map = {"dim": "http://www.dspace.org/xmlns/dspace/dim"}

csvfile = open('advisor-names_xml.csv', 'w')
csv_writer = csv.writer(csvfile)

for filename in files:
    with open(filename, 'r', encoding="utf-8") as content:
        tree = ET.parse(content)
        doc_root = tree.getroot()
        
        advisor_name=[]
        
        md_node = doc_root.find(".//dim:field[@element='contributor'][@qualifier='advisor']", prefix_map)
        
        def advisor_exist(name):
            md_node = doc_root.find(".//dim:field[@element='contributor'][@qualifier='advisor']", prefix_map)
            
            try:
                if md_node is None:
                    return ''
                return md_node.text.strip('.')
            except:
                return ''
        
        data = advisor_exist(md_node)
        #print(data)

        #normalize the sentence
        word_tokens = [word.lower() for word in data]
        #print(word_tokens)
        
        #converting word tokens to a string
        def listToString(word_tokens):
            _string = ' '.strip()
            return(_string.join(word_tokens))
        
        tokenized_string = listToString(word_tokens)
        #print(tokenized_string)
        
        advisor_name.append([tokenized_string])
        #print(advisor_name)
            
        csv_writer.writerow(advisor_name)

csvfile.close()