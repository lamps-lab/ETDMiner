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
year = ''
prefix_map = {"dim": "http://www.dspace.org/xmlns/dspace/dim"}

csvfile = open('title_xml.csv', 'w')
csv_writer = csv.writer(csvfile)

for filename in files:
    with open(filename, 'r', encoding="utf-8") as content:
        tree = ET.parse(content)
        doc_root = tree.getroot()
        
        ins_data=[]
        md_node = doc_root.find(".//dim:field[@element='title']", prefix_map)
        if md_node is not None:
            ins = md_node.text.strip('.').rstrip(',')
            print(ins)
            #tokenize the sentence
            sent_tokens = sent_tokenize(ins)
            #normalize the sentence
            sent_tokens = [sent.lower() for sent in sent_tokens]
            
            ins_data.append(sent_tokens)
            #print(program_data)
            
    csv_writer.writerow(ins_data)

csvfile.close()
#
#dfList=[]
##colname=['metadata_author']
#df=pd.read_csv('year_xml.csv')
#dfList.append(df)
#concatDf=pd.concat(dfList, axis=1)
##concatDf.columns=colname
#concatDf.to_csv('year_xml_modified.csv', index=None)
             

