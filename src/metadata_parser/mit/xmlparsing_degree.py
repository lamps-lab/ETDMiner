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
degree = ''
prefix_map = {"dim": "http://www.dspace.org/xmlns/dspace/dim"}

csvfile = open('degree_xml.csv', 'w')
csv_writer = csv.writer(csvfile)

for filename in files:
    with open(filename, 'r', encoding="utf-8") as content:
        tree = ET.parse(content)
        doc_root = tree.getroot()
        
        degree_data=[]
        md_node = doc_root.find(".//dim:field[@element='description'][@qualifier='degree']", prefix_map)
        if md_node is not None:
            degree = md_node.text
            #tokenize the sentence
            sent_tokens = sent_tokenize(degree)
            #normalize the sentence
            sent_tokens = [sent.lower() for sent in sent_tokens]
            print(sent_tokens)
            
            #degree_data.append(sent_tokens)
            #print(degree_data)
            
    csv_writer.writerow(sent_tokens)

csvfile.close()

#dfList=[]
#colname=['metadata_author']
#df=pd.read_csv('author-names_xml.csv', header = None)
#dfList.append(df)
#concatDf=pd.concat(dfList, axis=1)
#concatDf.columns=colname
#concatDf.to_csv('author-names_xml_modified.csv', index=None)
             

