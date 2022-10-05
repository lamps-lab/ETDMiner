#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  4 21:26:32 2022

@author: muntabir
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

hocr_path = 'hocr/*.html'

numbers = re.compile(r'(\d+)')
def numericalSort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts

hocr_files = sorted(glob.glob(hocr_path), key=numericalSort)

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

def normalized(values):
    norm = [(float(i) - min(values)) / (max(values) - min(values)) for i in values]
    return norm

class Features:
    
    def __init__(self, pos_dict):
        self.merged_dict = pos_dict

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
    pos_info = hocr_parser()
    pos_list = [item for sublist in pos_info for item in sublist]
    keys = ['x1','y1','x2','y2']
    pos = [dict((k, d[k]) for k in keys) for d in pos_list]
    
    feature = Features(pos)
    left_margin = feature.x1_feature()
    normalized_left_margin = normalized(left_margin)
    df2 = pd.DataFrame(normalized_left_margin)
    df2.to_csv("visual_features/left_margin_test.csv", index = None)
    
    yCoordinate1 = feature.y1_feature()
    normalized_yCoordinate1 = normalized(yCoordinate1)
    df3 = pd.DataFrame(normalized_yCoordinate1)
    df3.to_csv("visual_features/bottom_right_test.csv", index = None)


    yCoordinate2 = feature.y2_feature()
    normalized_yCoordinate2 = normalized(yCoordinate2)
    df4 = pd.DataFrame(normalized_yCoordinate2)
    df4.to_csv("visual_features/upper_left_test.csv", index = None)
    
    
    df1List=[]
    colname=['left_margin']
    df6 = pd.read_csv("visual_features/left_margin_test.csv", encoding='utf-8')
    df1List.append(df6)
    concatDf = pd.concat(df1List, axis =0)
    concatDf.columns=colname
    concatDf.to_csv("visual_features/left_margin_test-updated.csv", index = None)
    
    df2List=[]
    colname=['bottom_right']
    df7 = pd.read_csv("visual_features/bottom_right_test.csv", encoding='utf-8')
    df2List.append(df7)
    concatDf = pd.concat(df2List, axis =0)
    concatDf.columns=colname
    concatDf.to_csv("visual_features/bottom_right_test-updated.csv", index = None)
    
    df3List=[]
    colname=['upper_left']
    df8 = pd.read_csv("visual_features/upper_left_test.csv", encoding='utf-8')
    df3List.append(df8)
    concatDf = pd.concat(df3List, axis =0)
    concatDf.columns=colname
    concatDf.to_csv("visual_features/upper_left_test-updated.csv", index = None)
    

    df10 = pd.read_csv("visual_features/left_margin_test-updated.csv", encoding = 'utf-8')
    df11 = pd.read_csv("visual_features/bottom_right_test-updated.csv", encoding = 'utf-8')
    df12 = pd.read_csv("visual_features/upper_left_test-updated.csv", encoding = 'utf-8')
    
    result = pd.concat([df10, df11, df12], axis = 1, sort = False)
    result.to_csv("CRF_output/visual_features_test.csv", encoding = 'utf-8', index = None)