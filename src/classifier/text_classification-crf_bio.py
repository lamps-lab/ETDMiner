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
import os, os.path, sys
import glob
from xml.etree import ElementTree as ET
import numpy as np
from sklearn.metrics import classification_report
from nltk.tag import StanfordPOSTagger
import stanza

#csvfile = open('etd_to_bio.csv', 'w')
#csv_writer = csv.writer(csvfile)

def append_ann(files):
    xml_files = sorted(glob.glob(files+'/*.xml'))
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


def extract_features(doc):
    return [word2features(doc, i) for i in range(len(doc))]

def get_labels(doc):
    return [label for (token, postag, label) in doc]
    
def nlp_stanza_tokenize(document):
    tokenize_nlp = stanza.Pipeline('en', processors='tokenize')
    text_document = tokenize_nlp(document)
    sent_tokens = ""
    for i, sentence in enumerate(text_document.sentences):
        sent_tokens = [token.text for token in sentence.tokens]
    return (sent_tokens)

def nlp_stanza_pos(tokens):
    pos_nlp = stanza.Pipeline('en', processors='tokenize,mwt,pos', use_gpu=True, pos_batch_size=3000, tokenize_pretokenized=True)
    pos_document = pos_nlp((" ").join(tokens))
    sent_pos = [(word.xpos) for sent in pos_document.sentences for word in sent.words]
    return sent_pos

    
    
file_path = '/Users/muntabir/Documents/Project-Metadata-Extraction/annotated'
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
            temp = nlp_stanza_tokenize(withoutpunct)
            for token in temp:
                tags.append((token, other_tag))
        else:
            prev_tag = other_tag
            withoutpunct = remove_punct(word)
            temp = nlp_stanza_tokenize(withoutpunct)
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
# # # java_path = "/Users/muntabir/Library/Internet Plug-Ins/JavaAppletPlugin.plugin/Contents/Home/bin/java"
# # # os.environ['JAVAHOME'] = java_path

for i, doc in enumerate(docs):
    tokens = [t for t, label in doc]
    #print(tokens)
    tagged = nlp_stanza_pos(tokens)
    zipped = zip(tokens, tagged)
    #print(tuple(zipped))

    data.append([(w, pos, label) for (w, label), (word, pos) in zip(doc, zipped)])
    #print(data)


def word2features(doc, i):
    word = doc[i][0]
    postag = doc[i][1]
    
    features = [
            'word.lower='+ word.lower(),
            #'word[-3]=' + word[-3],
            #'word[-2]=' + word[-2],
            'word.isupper=%s' % word.isupper(),
            'word.istitle=%s' % word.istitle(),
            'word.isdigit=%s' % word.isdigit(),
            'postag=' + postag
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
            '-1:postag=' + postag1
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
            '+1:postag=' + postag1
        ])
    else:
        # Indicate that it is the 'end of a document'
        features.append('EOS')
        
    return features
        
# check = word2features(doc,i)
# print(check)

#Split to train and test sets
X = [extract_features(doc) for doc in data]
#print(X)
y = [get_labels(doc) for doc in data]        
#print(y)    
   
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

#train a CRF model
from sklearn_crfsuite import CRF
from sklearn_crfsuite import scorers
from sklearn_crfsuite import metrics
from collections import Counter

crf = CRF(
    algorithm='lbfgs',
    c1=0.1,
    c2=0.1,
    max_iterations=100,
    all_possible_transitions=True
)
crf.fit(X_train, y_train)
y_pred = crf.predict(X_test)

print(metrics.flat_classification_report(y_test, y_pred))

            
                
        




 
