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
from sklearn_crfsuite import CRF
from sklearn_crfsuite import metrics
import pickle
import pandas as pd

#csvfile = open('etd_to_bio.csv', 'w')
#csv_writer = csv.writer(csvfile)

numbers = re.compile(r'(\d+)')
def numericalSort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts


def append_ann(files):
    xml_files = sorted(glob.glob(files), key=numericalSort)
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
    return [label for (token, postag, left_margin, upper_left, bottom_right, label) in doc]
    
#def nlp_stanza_tokenize(document):
#     tokenize_nlp = stanza.Pipeline('en', processors='tokenize')
#     text_document = tokenize_nlp(document)
#     sent_tokens = ""
#     for i, sentence in enumerate(text_document.sentences):
#         sent_tokens = [token.text for token in sentence.tokens]
#     return (sent_tokens)
#
#def nlp_stanza_pos(tokens):
#     print("In stanza")
#     pos_nlp = stanza.Pipeline('en', processors='tokenize,pos', use_gpu=True, pos_batch_size=5000, tokenize_pretokenized=True)
#     pos_document = pos_nlp((" ").join(tokens))
#     sent_pos = [(word.xpos) for sent in pos_document.sentences for word in sent.words]
#     print("Out stanza")
#     return sent_pos

    
    
#file_path = '/home/hjayanet/Documents/Himarsha/LAMP-SYS/Annotated_Samples'
file_path = '/Users/muntabir/Documents/ETDmetadata/*.xml'
allxmlfiles = append_ann(file_path)
soup = bs(allxmlfiles, "html.parser")


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
            temp = word_tokenize(withoutpunct)
            for token in temp:
                tags.append((token, other_tag))
        else:
            prev_tag = other_tag
            withoutpunct = remove_punct(word)
            temp = word_tokenize(withoutpunct)
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
df = pd.read_csv("visual_features_test.csv", encoding='utf-8')
df.dropna(subset = ["tokens"], inplace=True)
df.drop(df.loc[df['tokens']=='<'].index, inplace=True)
df.drop(df.loc[df['tokens']=='document'].index, inplace=True)
df.drop(df.loc[df['tokens']=='/'].index, inplace=True)
left_margin = df['left_margin']
upper_left = df['upper_left']
bottom_right = df['bottom_right']

print("\n===================================\nBIO Tag Completed\n===================================\n") 

for i, doc in enumerate(docs):
    tokens = [t for t, label in doc]
    tagged = pos_tag(tokens)
    list_ = []
    for pos_ in tagged:
        list_.append(pos_[1])
    pos_tagged = list_
    left_margin = df['left_margin']
    upper_left = df['upper_left']
    bottom_right = df['bottom_right']
    zipped = zip(tokens, pos_tagged, left_margin, upper_left, bottom_right)
    
    data.append([(w, pos, left_margin, upper_left, bottom_right, label) for (w, label), (w, pos, left_margin, upper_left, bottom_right) in zip(doc, zipped)])

print("\n===================================\nPOS Tag Completed\n===================================\n")
print("\n===================================\nExtracting Features....\n===================================\n") 

def word2features(doc, i):
    word = doc[i][0]
    postag = doc[i][1]
    left_margin = doc[i][2]
    upper_left = doc[i][3]
    bottom_right = doc[i][4]
    
    features = [
            'bias',
            'word.lower='+ word.lower(),
            'word[-3:]=' + word[-3:],
            'word[-2:]=' + word[-2:],
            'word.isupper=%s' % word.isupper(),
            'word.istitle=%s' % word.istitle(),
            'word.isdigit=%s' % word.isdigit(),
            'left_margin=%s' % str(left_margin),
            'upper_left=%s' % str(upper_left),
            'bottom_right=%s' % str(bottom_right),
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
        left_margin1 = doc[i-1][2]
        upper_left1 = doc[i-1][3]
        bottom_right1 = doc[i-1][4]  
        features.extend([
            '-1:word.lower=' + word1.lower(),
            '-1:word.istitle=%s' % word1.istitle(),
            '-1:word.isupper=%s' % word1.isupper(),
            '-1:word.isdigit=%s' % word1.isdigit(),
            '-1:left_margin1=%s' % str(left_margin1),
            '-1:upper_left1=%s' % str(upper_left1),
            '-1:bottom_right1=%s' % str(bottom_right1),
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
        left_margin1 = doc[i+1][2]
        upper_left1 = doc[i+1][3]
        bottom_right1 = doc[i+1][4]
        features.extend([
            '+1:word.lower=' + word1.lower(),
            '+1:word.istitle=%s' % word1.istitle(),
            '+1:word.isupper=%s' % word1.isupper(),
            '+1:word.isdigit=%s' % word1.isdigit(),
            '+1:left_margin1=%s' % str(left_margin1),
            '+1:upper_left1=%s' % str(upper_left1),
            '+1:bottom_right1=%s' % str(bottom_right1),
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


X_test = [extract_features(doc) for doc in data]
y_test = [get_labels(doc) for doc in data]
print("\n===================================\nExtracting Features - Completed\n===================================\n")

#train a CRF model
print("\n===================================\nLoading CRF Model\n===================================\n")
filename = 'crf_model_visual.sav'

# load the model from disk
crf = pickle.load(open(filename, 'rb'))
labels = list(crf.classes_)
labels = labels.remove('O')
y_pred = crf.predict(X_test)

print(metrics.flat_f1_score(y_test, y_pred, average='weighted', labels=labels))
sorted_labels = sorted(labels, key=lambda name:(name[1:],name[0]))
print(metrics.flat_classification_report(y_test, y_pred, labels=sorted_labels, digits=3))

pred_list = []
#f = open("test-out.csv", "w")
for a, b in zip([p[1].split("=")[1] for p in X_test[len(X_test)-1]], y_pred[len(y_pred)-1]):
    pred_list.append((a, b))

dF = pd.DataFrame(pred_list)
dF.to_csv("test-out.csv", header = None, index=False)

#print(pred_list)
#    f.write("%s,%s\n" % (a, b))
print("\n===================================\nSaved Evaluation Result\n===================================\n")

################################################################################################################
#Avoid the below blocks of code

#print(metrics.flat_f1_score(y_test, y_pred, average='weighted', labels=labels))
#
##inspect per-class results in more details: full classification result 
#sorted_labels = sorted(labels, key=lambda name:(name[1:],name[0]))
#print(metrics.flat_classification_report(y_test, y_pred, labels=sorted_labels, digits=3))


#f = open("out_test.csv", "w")
#for a, b in zip([p[1].split("=")[1] for p in X_test[len(X_test)-1]], y_pred[len(y_pred)-1]):
# 	f.write("%s\t%s\n" % (a, b))
#
#f.close()
#print("\n===================================\nSaved Result on Test Samples with BIO Tags\n===================================\n")


# labels = list(crf.classes_)
# labels.remove('O')
# sorted_labels = sorted(labels, key=lambda name:(name[1:],name[0]))
# y_pred = crf.predict(X_test)
# result = metrics.flat_classification_report(y_test, y_pred,labels=sorted_labels, digits=3)
# print(result)
#mlb = MultiLabelBinarizer(sparse_output=True)
#mlb.fit_transform(X_test)
#mlb.fit_transform(y_test)
#print(metrics.flat_classification_report(X_test, y_test, labels=sorted_labels, digits=3))

# def print_state_features(state_features):
#     for (attr, label), weight in state_features:
#         print("%0.6f %-8s %s" % (weight, label, attr))

# print("Top positive:")
# print(print_state_features(Counter(crf.state_features_).most_common(30)))

# print("\nTop negative:")
# print(print_state_features(Counter(crf.state_features_).most_common()[-30:]))
################################################################################################