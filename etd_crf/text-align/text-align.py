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
import nltk
from nltk import word_tokenize


clean = '/Users/muntabir/Documents/etdExtraction/etd_crf_result/text-align/annotated-test/*.xml'
noisy_hocr = '/Users/muntabir/Documents/etdExtraction/etd_crf_result/text-align/hocr/*.html'


numbers = re.compile(r'(\d+)')
def numericalSort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts


target_files = sorted(glob.glob(clean), key=numericalSort)
hocr_files = sorted(glob.glob(noisy_hocr), key=numericalSort)


def hocr_parser():
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
                
            return tokens_bbox

def ann():
    for files in target_files:
        new_data = b''
        data = ET.parse(files).getroot()
        temp = ET.tostring(data)
        new_data = new_data+temp
    return new_data


def parser(text):
    regex = r'(<\S*?>)*(\w+[^<>]*?\w)(<\S*?>)(\s?|<\S*?>?|\,?|\, ?|\n?)(\n?\w.?[^<]*|[>]?\.*[\s?]*\n)'
    pattern = re.compile(regex)
    html = text.decode('utf-8')
    doc = re.findall(pattern, html)
    return doc
    

def tuplesTolist(tuple_text):
    list_of_tuples = list(map(list, tuple_text))
    flat_list = [item for sublist in list_of_tuples for item in sublist]
    return flat_list

def listToString(text):
        _string = ""
        return _string.join(text)

def align(text):
    stopwords = ['<title>', '</title>', '<author>', '</author>', '<university>', '</university>', '<degree>', '</degree>', '<advisor>', '\n',
             '</advisor>', '<year>', '</year>', '<program>', '</program>']
    result_list = [word for word in text if word not in stopwords]
    token_list = []
    for items in result_list:
        tokens = word_tokenize(items)
        token_list.append(tokens)
    
    flat_list = [item for sublist in token_list for item in sublist]
    target_ = [words for words in flat_list]
    target_ = " ".join(target_)
        
    
    query_text = hocr_parser()
    query_ = [texts['text'].replace("\n"," ").strip() for texts in query_text]
    query_ = " ".join(query_)

    
    result = edlib.align(query_, target_, task="path", additionalEqualities=[])
    alignment = edlib.getNiceAlignment(result, query_, target_)
    aligned = alignment['target_aligned']
    return aligned


def merge(lines, pos):
    l3 = [{**u, **v} for u, v in zip_longest(lines, pos, fillvalue={})]
    return l3


ann_text = ann()

target_text = parser(ann_text)
#print(target_text)

convert_tuples = tuplesTolist(target_text)

text_align = align(convert_tuples)

tokenized = text_align.split()
#print(tokenized)

lines = []
for elements in tokenized:
    lines.append({"text":elements})
#print(lines)

pos_info = hocr_parser()

keys = ['x1','y1','x2','y2']
pos = [dict((k, d[k]) for k in keys) for d in pos_info]
##print(pos[0].values())
#
merged = merge(lines, pos)
print(merged)



