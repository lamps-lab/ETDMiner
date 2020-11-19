#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
Created on Tue 11th Jun
@author: Muntabir Choudhury
updated - added leventiens distance, and using pandas DataFrame to correctly matching
"""

#This code is used to compare the metadata groundtruth vs the processed predicted output from the CRF model (output from the code process_crf_output.py).


import pandas as pd
import os, os.path
import sys
import glob
import re
import csv
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

dfList=[]
colname=['predicted-title']
df1 = pd.read_csv("prtitle.csv", encoding='utf-8', header=None) #glued predicted tokens
dfList.append(df1)
concatDf = pd.concat(dfList, axis =0)
concatDf.columns=colname
concatDf.to_csv('pr_title.csv', index = None, header=True, encoding = 'utf-8') #actual predicted title with header

dfList1=[]
colname=['gt-title']
df2 = pd.read_csv("title_gt.csv", encoding ='utf-8', header=None) #original one
dfList1.append(df2)
concatDf = pd.concat(dfList1, axis =0)
concatDf.columns=colname
concatDf.to_csv('gt_title.csv', index = None, header=True, encoding = 'utf-8') #ground truth title with header

#print(df1)
#print(df2)


df3 = pd.read_csv('pr_title.csv', encoding='utf-8')
#print(df3)
df4 = pd.read_csv('gt_title.csv', encoding='utf-8')
#print(df4)


df5 = pd.DataFrame(columns=['crf_match'])
df5['crf_match'] = df3['predicted-title'].eq(df4['gt-title']).replace([True, False], [1,0])
result = pd.concat([df3, df4, df5], axis = 1, sort = False)
result.to_csv('title_outfile.csv', index = None, header=True, encoding = 'utf-8') #contains the binary match between predicted title and ground truth title

df6 = pd.read_csv('title_outfile.csv', encoding = 'utf-8')
count = df6['crf_match'].value_counts()
print(count)

def fuzzy_merge(df_1, df_2, key1, key2, threshold=95, limit=2):
    """
    :param df_1: the left table to join
    :param df_2: the right table to join
    :param key1: key column of the left table
    :param key2: key column of the right table
    :param threshold: how close the matches should be to return a match, based on Levenshtein distance
    :param limit: the amount of matches that will get returned, these are sorted high to low
    :return: dataframe with boths keys and matches
    """
    s = df_2[key2].tolist()

    m = df_1[key1].apply(lambda x: process.extract(x, s, limit=limit))    
    df_1['matches'] = m

    m2 = df_1['matches'].apply(lambda x: ', '.join([i[0] for i in x if i[1] >= threshold]))
    df_1['matches'] = m2
    
    m3 = pd.DataFrame(columns=['loose_match'])
    m3['loose_match'] = df_2[key2].eq(df_1['matches']).replace([True, False], [1,0])
                                 
    return m3

df = fuzzy_merge(df4, df3, 'gt-title', 'predicted-title')
df.to_csv("loose-match.csv", index = None, header=True, encoding = 'utf-8')

df7 = pd.read_csv('loose-match.csv', encoding = 'utf-8')
count = df7['loose_match'].value_counts()
print(count)

result = pd.concat([df6,df7], axis = 1, sort = False)
result.to_csv("title_match.csv", index = None, header=True, encoding = 'utf-8')