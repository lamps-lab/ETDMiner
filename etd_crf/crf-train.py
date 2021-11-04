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
import scipy.stats
from sklearn_crfsuite import CRF
from sklearn_crfsuite import metrics

from sklearn.metrics import make_scorer
import pickle
# from collections import Counter
# from sklearn.metrics import make_scorer
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import cross_val_score 

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
    return [label for token, postag, label in doc]
    
# def nlp_stanza_tokenize(document):
#     tokenize_nlp = stanza.Pipeline('en', processors='tokenize')
#     text_document = tokenize_nlp(document)
#     sent_tokens = ""
#     for i, sentence in enumerate(text_document.sentences):
#         sent_tokens = [token.text for token in sentence.tokens]
#     return (sent_tokens)

# def nlp_stanza_pos(tokens):
#     pos_nlp = stanza.Pipeline('en', processors='tokenize,pos', use_gpu=True, pos_batch_size=3000, tokenize_pretokenized=True)
#     pos_document = pos_nlp((" ").join(tokens))
#     sent_pos = [(word.xpos) for sent in pos_document.sentences for word in sent.words]
#     return sent_pos

    
    
file_path = '/Users/muntabir/Documents/Annotated/train/*.xml'
allxmlfiles = append_ann(file_path)
soup = bs(allxmlfiles, "html.parser")

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
        
data = []

print("\n===================================\nBIO Tag Completed\n===================================\n") 

from collections import Counter
for i, doc in enumerate(docs):
    tokens = [t for t, label in doc]
    #print(tokens)
    tagged = pos_tag(tokens)
    counter = Counter(tag for word, tag in tagged)
    #print(counter)
    #zipped = zip(tokens, tagged)
    #print(tuple(zipped))

    data.append([(w, pos, label) for (w, label), (word, pos) in zip(doc, tagged)])



print("\n===================================\nPOS Tag Completed\n===================================\n") 

print("\n===================================\nExtracting Features....\n===================================\n") 
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

print("\n===================================\nExtracting Features - Completed\n===================================\n")        
# check = word2features(doc,i)
# print(check)

X_train = [extract_features(doc) for doc in data]
y_train = [get_labels(doc) for doc in data]    
   
#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state= 0)

print("\n===================================\nTraining CRF Model\n===================================\n")


#train a CRF model
crf = CRF(
    algorithm='lbfgs',
    c1=0.1,
    c2=0.1,
    max_iterations=100,
    all_possible_transitions=True
)

crf.fit(X_train, y_train)

print("\n===================================\nModel Saved\n===================================\n")
#dump the model
filename = 'crf_model.sav'
pickle.dump(crf, open(filename, 'wb'))


# params_space = {
#     'c1': scipy.stats.expon(scale=0.1),
#     'c2': scipy.stats.expon(scale=0.01),
# }
# labels = crf.classes_

# f1_scorer = make_scorer(metrics.flat_f1_score,
#                         average='weighted', labels=labels)

# print("\n===================================\nTuning Hyperparameter with 5 fold cross validation\n===================================\n")
# rs = RandomizedSearchCV(crf, params_space, cv=5,
#                         verbose=1,
#                         n_jobs=-1,
#                         scoring=f1_scorer)
# rs.fit(X_train, y_train)

#






# print("\n===================================\nEvaluation Result\n===================================\n")
# #evaluation
# """Since there are more O-tags entities in the dataset, but we are interested in other entities which is labeled by following the
# BIO schema. To account for this we'll use averaged F-1 score computed for all labels except for O. 
# """
# labels = list(crf.classes_)
# labels.remove('O')
# y_pred = crf.predict(X_test)

# print("\n===================================\nEvaluation Done\n===================================\n")

# print(metrics.flat_f1_score(y_test, y_pred, average='weighted', labels=labels))

# #inspect per-class results in more details: full classification result 
# sorted_labels = sorted(labels, key=lambda name:(name[1:],name[0]))
# print(metrics.flat_classification_report(y_test, y_pred, labels=sorted_labels, digits=3))



# f = open("predict-out.csv", "w")
# for a, b in zip([p[1].split("=")[1] for p in X_test[len(X_test)-1]], y_pred[len(y_pred)-1]):
#  	f.write("%s,%s\n" % (a, b))
# f.close()
# print("\n===================================\nPredicted Result Saved with BIO Tags\n===================================\n")

##########################################################################################
# # def print_transitions(trans_features):
# #     for (label_from, label_to), weight in trans_features:
# #         print("%-6s -> %-7s %0.6f" % (label_from, label_to, weight))
        
# # print("Top likely transitions:")
# # print(print_transitions(Counter(crf.transition_features_).most_common(20)))
# # print("\nTop unlikely transitions:")
# # print(print_transitions(Counter(crf.transition_features_).most_common()[-20:]))

# # #check the state features
# # def print_state_features(state_features):
# #     for (attr, label), weight in state_features:
# #         print("%0.6f %-8s %s" % (weight, label, attr))

# # print("Top positive:")
# # print(print_state_features(Counter(crf.state_features_).most_common(50)))

# # print("\nTop negative:")
# # print(print_state_features(Counter(crf.state_features_).most_common()[-50:]))
#########################################################################################
