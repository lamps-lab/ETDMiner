# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 13:20:47 2020
@author: Muntabir Choudhury

Modified by:+++++++
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
import os, os.path, sys
import glob
from xml.etree import ElementTree as ET
import numpy as np
from sklearn.metrics import classification_report
from nltk.tag import StanfordPOSTagger
#import stanza
from sklearn_crfsuite import CRF
from sklearn_crfsuite import metrics
import pickle
import sys


#csvfile = open('etd_to_bio.csv', 'w')
#csv_writer = csv.writer(csvfile)

CRFmodel_filename = sys.argv[1]

numbers = re.compile(r'(\d+)')

def numericalSort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts

#this function removes special characters and punctuations
def remove_punct(withpunct):
    punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
    without_punct = ""
    char = 'nan'
    for char in withpunct:
        if char not in punctuations:
            without_punct = without_punct + char
    return(without_punct)

def extract_features(doc):
    #print(doc[0],i)
    return [word2features(doc, i) for i in range(len(doc))]

def get_labels(doc):
    return [label for (token, postag, label) in doc]


def word2features(doc, i):
    word = doc[i][0]
    postag = doc[i][1]   
    features = [
            'bias',
            'word.lower='+ word.lower(),
            'word[-3:]=' + word[-3:],
            'word[-2:]=' + word[-2:],
            'word.isupper=%s' % word.isupper(),
            'word.istitle=%s' % word.istitle(),
            'word.isdigit=%s' % word.isdigit(),
            'postag=' + postag,
            'postag[:2]=' + postag[:2],
            'postag[:3]=' + postag[:3],
            'postag[-2:]=' + postag[-2:],
            'postag[-3:]=' + postag[-3:],
            'wordlength=%s' % len(word),
            'wordmixedcap=%s' % len([x for x in word[1:] if x.isupper()])
            ]
    #features for words that are not at the begining of the document
    if i > 0:
        word1 = doc[i-1][0]
        postag1 = doc[i-1][1]
        features.extend([
            '-1:word.lower=' + word1.lower(),
            '-1:word.istitle=%s' % word1.istitle(),
            '-1:word.isupper=%s' % word1.isupper(),
            '-1:word.isdigit=%s' % word1.isdigit(),
            '-1:postag=' + postag1,
            '-1:postag[:2]='+ postag1[:2],
            '-1:postag[:3]=' + postag1[:3],
            '-1:postag[-2:]=' + postag1[-2:],
            '-1:postag[-3:]=' + postag1[-3:],
            '-1:wordlength=%s' % len(word1),
            '-1:wordmixedcap=%s' % len([x for x in word1[1:] if x.isupper()])
            ])
    else:
        #indicate that it is the begining of a document
        features.append('BOS')       
    #Features that are not at the end of the document
    if i < len(doc)-1:
        word1 = doc[i+1][0]
        postag1 = doc[i+1][1]
        features.extend([
            '+1:word.lower=' + word1.lower(),
            '+1:word.istitle=%s' % word1.istitle(),
            '+1:word.isupper=%s' % word1.isupper(),
            '+1:word.isdigit=%s' % word1.isdigit(),
            '+1:postag=' + postag1,
            '+1:postag[:2]=' + postag1[:2],
            '+1:postag[:3]=' + postag1[:3],
            '+1:postag[-2:]=' + postag1[-2:],
            '+1:postag[-3:]=' + postag1[-3:],
            '+1:wordlength=%s' % len(word1),
            '+1:wordmixedcap=%s' % len([x for x in word1[1:] if x.isupper()])
        ])
    else:
        # Indicate that it is the 'end of a document'
        features.append('EOS')     
    return features

def predict_metadata(xml_file):
    soup = bs(xml_file, "html.parser")

    #identify the tagged element
    docs = []
    sents = []

    for d in soup.find_all("document"):
        for word in d:
            tags = []
            NoneType = type(None)
            other_tag = 'O'
            if isinstance(word.name, NoneType) == True:
                withoutpunct = remove_punct(word)
                temp = withoutpunct.split()
                for token in temp:
                    tags.append((token, other_tag))
            else:
                prev_tag = other_tag
                withoutpunct = remove_punct(word)
                temp = withoutpunct.split()
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
    #print(docs)  
    data = []

    #print("\n===================================\nBIO Tag Completed\n===================================\n") 

    for i, doc in enumerate(docs):
        tokens = [t for t, label in doc]
        tagged = pos_tag(tokens)

        data.append([(w, pos, label) for (w, label), (word, pos) in zip(doc, tagged)])
        #print(data)

    #print("\n===================================\nPOS Tag Completed\n===================================\n")
    #print("\n===================================\nExtracting Features....\n===================================\n") 


    #Split to train and test sets

    X_test = [extract_features(doc) for doc in data]
    y_test = [get_labels(doc) for doc in data]
    #print("\n===================================\nExtracting Features - Completed\n===================================\n")


    #train a CRF model
    #print("\n===================================\nLoading CRF Model\n===================================\n")

    # load the model from disk
    crf = pickle.load(open(CRFmodel_filename, 'rb'))
    labels = list(crf.classes_)
    labels.remove('O')
    y_pred = crf.predict(X_test)
    return X_test, y_pred




# file_path = f"xml/*.xml"
# allxmlfiles = append_ann(file_path)
# soup = bs(allxmlfiles, "html.parser")


# def append_ann(files):
#     xml_files = sorted(glob.glob(files), key=numericalSort)
#     new_data = b""
#     for xml_file in xml_files:
#         print(xml_file)
#         data = ET.parse(xml_file).getroot()
#         temp = ET.tostring(data)
#         new_data = new_data+temp
#     print(new_data)
#     return new_data


if __name__ == "__main__":
    # with open("CRF_output/intermediate.csv","w") as g:
    #     pass
    with open("CRF_output/intermediate.csv","w") as f:
        file_path = f"xml/*.xml"
        xml_files = sorted(glob.glob(file_path), key=numericalSort)
        for xml_file in xml_files:
            #print(xml_file)
            #xml/10001.xml
            new_data = b""
            etdid = xml_file.split("/")[1].strip(".xml")
            data = ET.parse(xml_file).getroot()
            temp = ET.tostring(data)
            new_data = new_data+temp
            #print(new_data)
            X_test1, y_pred1 = predict_metadata(new_data)
            #print("\n===================================\nGenerating output\n===================================\n")
            for a, b in zip([p[1].split("=")[1] for p in X_test1[len(X_test1)-1]], y_pred1[len(y_pred1)-1]):
                #print(a,b)
                f.write("%s,%s,%s\n" % (etdid,a, b))