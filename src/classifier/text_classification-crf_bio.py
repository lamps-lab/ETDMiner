# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 13:20:47 2020

@author: Muntabir Choudhury

"""
#invoke libraries
from bs4 import BeautifulSoup as bs
from bs4.element import Tag
import csv
import os
import codecs
import re
import nltk
from nltk import word_tokenize
from nltk import pos_tag
from sklearn.model_selection import train_test_split
import pycrfsuite
import os, os.path, sys
import glob
from xml.etree import ElementTree as ET
import numpy as np
from sklearn.metrics import classification_report
from nltk.tag import StanfordPOSTagger
#import nltk.tag.stanford as st


csvfile = open('etd_to_bio.csv', 'w')
csv_writer = csv.writer(csvfile)

def append_ann(files):
    xml_files = sorted(glob.glob(files+'\*.xml'))
    #xml_element_tree = None
    new_data = b""
    for xml_file in xml_files:
        data = ET.parse(xml_file).getroot()
        temp = ET.tostring(data)
        new_data = new_data+temp
    return new_data



#this function removes special characters and punctuations
def remove_punct(withpunct):
    punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
    without_punct = ""
    char = 'nan'
    for char in withpunct:
        if char not in punctuations:
            without_punct = without_punct + char
    return(without_punct)


#def extract_features(doc):
#    return [word2features(doc, i) for i in range(len(doc))]
#
def get_labels(doc):
    return [label for (token, postag, label) in doc]
    
file_path = r'C:\Users\Muntabir\nltk_data\corpora\cookbook\clean_data\annotated'
allxmlfiles = append_ann(file_path)
soup = bs(allxmlfiles, "html5lib")

#idenmtify the tagged element
docs = []
sents = []

for d in soup.find_all("document"):
    for word in d:
        tags = []
        NoneType = type(None)
        other_tag = 'O'
        if isinstance(word.name, NoneType) == True:
            withoutpunct = remove_punct(word)
            temp = word_tokenize(withoutpunct)
            #word_norm = [word.lower() for word in temp]
            for token in temp:
                tags.append((token, other_tag))
        else:
            prev_tag = other_tag
            withoutpunct = remove_punct(word)
            temp = word_tokenize(withoutpunct)
            #word_norm = [word.lower() for word in temp]
            for token in temp:
                #beginning of the token
                if tags != 'O' and prev_tag == 'O' :
                    tags.append((token, "B-"+word.name)) 
                    tag = "B-"+word.name
                    prev_tag = tag
                #inside of the token
                elif prev_tag != 'O' and prev_tag == tag:
                    tags.append((token, "I-"+word.name))
                    tag = "I-"+word.name
                    prev_tag = tag
                #adjacent of the token
                elif prev_tag != 'O' and prev_tag != tag:
                    tags.append((token, "B-"+word.name))
                    tag = "B-"+word.name
                    prev_tag = tag
                         
        sents = sents + tags
        docs.append(sents)
        
data = []
java_path = r"C:\Program Files\Java\jre1.8.0_181\bin\java.exe"
os.environ['JAVAHOME'] = java_path

for i, doc in enumerate(docs):
    tokens = [t for t, label in doc]
    path_to_model = r"C:\Users\Muntabir\stanford-postagger\models\english-bidirectional-distsim.tagger"
    path_to_jar = r"C:\Users\Muntabir\stanford-postagger\stanford-postagger.jar"
    pos_tagger = StanfordPOSTagger(model_filename=path_to_model, path_to_jar=path_to_jar)
    tagged = pos_tagger.tag(tokens)
    #tagged = pos_tag(tokens)
    #print(tagged)
    
    data.append([(w, pos, label) for (w, label), (word, pos) in zip(doc, tagged)])
    print(data)
    
#    csv_writer.writerow(data)
#
#csvfile.close()

#def word2features(doc, i):
#    word = doc[i][0]
#    postag = doc[i][1]
#    
#    features = [
#            'bias',
#            'word.lower='+word.lower(),
#            'word.isupper=%s' % word.isupper(),
#            'word.istitle=%s' % word.istitle(),
#            'word.isdigit=%s' % word.isdigit(),
#            'postag=' + postag
#            ]
#    #features for words that are not at the begining of the document
#    if i > 0:
#        word1 = doc[i-1][0]
#        postag1 = doc[i-1][1]
#        features.extend([
#            '-1:word.lower=' + word1.lower(),
#            '-1:word.istitle=%s' % word1.istitle(),
#            '-1:word.isupper=%s' % word1.isupper(),
#            '-1:word.isdigit=%s' % word1.isdigit(),
#            '-1:postag=' + postag1
#            ])
#    else:
#        #indicate that it is the begining of a document
#        features.append('BOS')
#    
#    if i < len(doc)-1:
#        word1 = doc[i+1][0]
#        postag1 = doc[i+1][1]
#        features.extend([
#            '+1:word.lower=' + word1.lower(),
#            '+1:word.istitle=%s' % word1.istitle(),
#            '+1:word.isupper=%s' % word1.isupper(),
#            '+1:word.isdigit=%s' % word1.isdigit(),
#            '+1:postag=' + postag1
#        ])
#    else:
#        # Indicate that it is the 'end of a document'
#        features.append('EOS')
#        
#    return features
        
#check = word2features(doc,i)
#print(check)
        
    
   
    


            
                
        




 
