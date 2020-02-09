# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 03:51:15 2020

@author: Muntabir Choudhury 
"""
from nltk.tokenize import sent_tokenize
import glob
import csv
import xml.etree.ElementTree as ET

path = r"C:\Users\Muntabir\Documents\Graduate School_ODU\RA\MIT_Sample\etd_metadata_xml"
files = glob.glob("*.xml")
author = ''
prefix_map = {"dim": "http://www.dspace.org/xmlns/dspace/dim"}

csvfile = open('author-names_xml.csv', 'w')
csv_writer = csv.writer(csvfile)

for filename in files:
    with open(filename, 'r', encoding="utf-8") as content:
        tree = ET.parse(content)
        doc_root = tree.getroot()
        
        author_name=[]
        md_node = doc_root.find(".//dim:field[@element='contributor'][@qualifier='author']", prefix_map)
        if md_node is not None:
            author = md_node.text
            #tokenize the sentence
            sent_tokens = sent_tokenize(author)
            #normalize the sentence
            sent_tokens = [sent.lower() for sent in sent_tokens]
            
            author_name.append(sent_tokens)
            
    csv_writer.writerow(author_name)

csvfile.close()
             

