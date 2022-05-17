#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  7 18:37:26 2021
@author: Muntabir Choudhury
"""


#import libraries
import bs4
import edlib
import glob
import re
from xml.etree import ElementTree as ET
from itertools import zip_longest
from nltk import word_tokenize
import pandas as pd


clean = '/Users/muntabir/Documents/etdExtraction/etd_crf_result/text-align/annotated-train/*.xml'
noisy_hocr = '/Users/muntabir/Documents/etdExtraction/etd_crf_result/text-align/hocr/hocr-train/*.html'


numbers = re.compile(r'(\d+)')
def numericalSort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts


target_files = sorted(glob.glob(clean), key=numericalSort)
hocr_files = sorted(glob.glob(noisy_hocr), key=numericalSort)

## This function will extract all the position information for each token from the hOCR files 
# and return it as a list 
def hocr_parser():
    list_ = []
    for files in hocr_files:
        with open(files, mode='r', encoding='utf-8') as html_input:
            soup = bs4.BeautifulSoup(html_input,'lxml')
            ocr_words = soup.findAll("span", {"class": "ocrx_word"})
            tokens_bbox = []
            for line in ocr_words:
                words = line.text.replace("\n"," ").strip()
                title = line['title']
                #The coordinates of the bounding box
                x1,y1,x2,y2 = map(int, title[5:title.find(";")].split())
                tokens_bbox.append({"x1":x1,"y1":y1,"x2":x2,"y2":y2,"text": words})
            
            list_.append(tokens_bbox)
                           
    return list_


## This function will read all the annotated files and return it as a list
def ann():
    list_ = []
    for files in target_files:
        new_data = b''
        data = ET.parse(files).getroot()
        temp = ET.tostring(data)
        new_data = new_data+temp    
        list_.append(new_data)
    
    return list_

## This function will parse all the tags from the annotated text files (i.e. xml files) using regular expression
# and return it as a list
def parser(text):
    list_ = []
    for sent in text:
        regex = r'(<\S*?>)*(\w+[^<>]*?\w)(<\S*?>)(\s?|<\S*?>?|\,?|\, ?|\n?)(\n?\w.?[^<]*|[>]?\.*[\s?]*\n)'
        pattern = re.compile(regex)
        html = sent.decode('utf-8')
        doc = re.findall(pattern, html)
        list_.append(doc)
    
    return list_
    
## This is a preprocessing function which converts list of tuples to a flat list
def tuplesTolist(tuple_text):
    list_ = []
    for elements in tuple_text:
        #print(elements)
        list_of_tuples = list(map(list, elements))
        flat_list = [item for sublist in list_of_tuples for item in sublist]
        list_.append(flat_list)

    return list_

## This function will convert list to string
def listToString(text):
        _string = ""
        return _string.join(text)

## This function will align all the noisy tokens and clean text tokens using edlib python wrapper
def align(text):
    target_list = []
    for elements in text:
        stopwords = ['<document>', '</document>', '<title>', '</title>', '<author>', '</author>', '<university>', '</university>', '<degree>', '</degree>', '<advisor>', '\n',
                     '</advisor>', '<year>', '</year>', '<program>', '</program>', '<', '/', 'document']
        result_list = [word for word in elements if word not in stopwords]
        token_list = []
        for items in result_list:
            tokens = word_tokenize(items)
            token_list.append(tokens)
    
        flat_list = [item for sublist in token_list for item in sublist]
    
        for target_text in flat_list:
            target_list.append(target_text)      
    
    target_ = " ".join(target_list)
        
    list_query = hocr_parser()
    query_list = []
    for l in list_query:
        for texts in l:
            query_text = texts['text']
            query_list.append(query_text)
   
    query_ = " ".join(query_list)
  
    result = edlib.align(query_, target_, task="path", additionalEqualities=[])
    alignment = edlib.getNiceAlignment(result, query_, target_)
    aligned = alignment['target_aligned']
    return aligned

## This function save all the aligned tokens into dictionary
def token_dict(tokens):
    lines = []
    for elements in tokenized:
        lines.append({"aligned-token":elements})
    return lines

## This function will map all the aligned tokens with the postion information and return the result as a list of dictionaries
def merge(lines, pos):
    l3 = [{**u, **v} for u, v in zip_longest(lines, pos, fillvalue={})]
    return l3


def normalized(values):
    norm = [(float(i) - min(values)) / (max(values) - min(values)) for i in values]
    return norm

class Features:
    
    def __init__(self, merged_dict):
        self.merged_dict = merged_dict
        #self.normalize = normalize

    def x1_feature(self):
        x1_list = []
        for values in self.merged_dict:
            x1_features = values['x1']
            x1_list.append(x1_features)
        return x1_list
    
    def y1_feature(self):
        y1_list = []
        for values in self.merged_dict:
            y1_features = values['y1']
            y1_list.append(y1_features)
        return y1_list
    
    def y2_feature(self):
        y2_list = []
        for values in self.merged_dict:
            y2_features = values['y2']
            y2_list.append(y2_features)
        return y2_list
    

if __name__ == "__main__":
    ann_text = ann()
    
    target_text = parser(ann_text)

    convert_tuples = tuplesTolist(target_text)

    text_align = align(convert_tuples)

    tokenized = text_align.split()
    df1 = pd.DataFrame(tokenized)
    df1.to_csv("tokenized_string.csv", encoding = 'utf-8', index = None)
    
    tokens = token_dict(tokenized)
   
    ## Reading the hOCR parsed files and saving all the keys to a dictionary
    pos_info = hocr_parser()
    pos_list = [item for sublist in pos_info for item in sublist]
    keys = ['x1','y1','x2','y2']
    pos = [dict((k, d[k]) for k in keys) for d in pos_list]

    ## mapping all the position information keys and aligned-token into a one single dictionary by calling the merge function 
    merged = merge(tokens, pos)

    feature = Features(merged)
    left_margin = feature.x1_feature()
    normalized_left_margin = normalized(left_margin)
    df2 = pd.DataFrame(normalized_left_margin)
    df2.to_csv("left_margin.csv", index = None)
    
    yCoordinate1 = feature.y1_feature()
    normalized_yCoordinate1 = normalized(yCoordinate1)
    df3 = pd.DataFrame(normalized_yCoordinate1)
    df3.to_csv("bottom_right.csv", index = None)
    #print(normalized_yCoordinate1)
    yCoordinate2 = feature.y1_feature()
    normalized_yCoordinate2 = normalized(yCoordinate2)
    df4 = pd.DataFrame(normalized_yCoordinate2)
    df4.to_csv("upper_left.csv", index = None)
    

    dfList=[]
    colname=['tokens']
    df5 = pd.read_csv("tokenized_string.csv", encoding='utf-8')
    dfList.append(df5)
    concatDf = pd.concat(dfList, axis =0)
    concatDf.columns=colname
    concatDf.to_csv("tokenized_string-train.csv", index = None)
    
    df1List=[]
    colname=['left_margin']
    df6 = pd.read_csv("left_margin.csv", encoding='utf-8')
    df1List.append(df6)
    concatDf = pd.concat(df1List, axis =0)
    concatDf.columns=colname
    concatDf.to_csv("left_margin-train.csv", index = None)
    
    df2List=[]
    colname=['bottom_right']
    df7 = pd.read_csv("bottom_right.csv", encoding='utf-8')
    df2List.append(df7)
    concatDf = pd.concat(df2List, axis =0)
    concatDf.columns=colname
    concatDf.to_csv("bottom_right-train.csv", index = None)
    
    df3List=[]
    colname=['upper_left']
    df8 = pd.read_csv("upper_left.csv", encoding='utf-8')
    df3List.append(df8)
    concatDf = pd.concat(df3List, axis =0)
    concatDf.columns=colname
    concatDf.to_csv("upper_left-train.csv", index = None)
    
    df9 = pd.read_csv("tokenized_string-train.csv", encoding = 'utf-8')
    df10 = pd.read_csv("left_margin-train.csv", encoding = 'utf-8')
    df11 = pd.read_csv("bottom_right-train.csv", encoding = 'utf-8')
    df12 = pd.read_csv("upper_left-train.csv", encoding = 'utf-8')
    
    result = pd.concat([df9, df10, df11, df12], axis = 1, sort = False)
    result.to_csv("visual_features_train.csv", encoding = 'utf-8', index = None)
#    
    

    

    

        
    



