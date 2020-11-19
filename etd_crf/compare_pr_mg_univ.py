#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 04:18:00 2020

@author: muntabir
"""


import pandas as pd
import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

dfList=[]
colname=['predicted-university']
df1 = pd.read_csv("pruniv.csv", encoding='utf-8', header=None) #glued predicted tokens
dfList.append(df1)
concatDf = pd.concat(dfList, axis =0)
concatDf.columns=colname
concatDf.to_csv('pr_univ.csv', index = None, header=True, encoding = 'utf-8') #actual predicted title with header

dfList1=[]
colname=['gt-university']
df2 = pd.read_csv("university_gt.csv", encoding ='utf-8', header=None)
dfList1.append(df2)
concatDf = pd.concat(dfList1, axis =0)
concatDf.columns=colname
concatDf.to_csv('gt_univ.csv', index = None, header=True, encoding = 'utf-8') #actual ground truth title with header


df3 = pd.read_csv('pr_univ.csv', encoding='utf-8')
#print(df3)
df4 = pd.read_csv('gt_univ.csv', encoding='utf-8')
#print(df4)


df3['predicted-university']=df3['predicted-university'].replace("\s*",regex=True)
df4['gt-university']=df4['gt-university'].replace("\s*,'",regex=True)


df5 = pd.DataFrame(columns=['match'])
df5['match'] = df3['predicted-university'].eq(df4['gt-university']).replace([True, False], [1,0])
result = pd.concat([df3, df4, df5], axis = 1, sort = False)
result.to_csv('university_outfile.csv', index = None, header=True, encoding = 'utf-8') #contains the binary match between predicted title and ground truth title

df6 = pd.read_csv('university_outfile.csv', encoding = 'utf-8')
count = df6['match'].value_counts()
print(count)

str1 = df6['predicted-university'].unique()
#print(str1)
str2 = df6['gt-university'].unique()
#print(str2)

ratio = fuzz.ratio(str1,str2)
partial_ratio = fuzz.partial_ratio(str1,str2)
print(ratio)
print(partial_ratio)

def fuzzy_merge(df_1, df_2, key1, key2, threshold=81, limit = 1):
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

    m = df_1[key1].apply(lambda x: process.extract(x, s, limit = limit))  
    df_1['matches'] = m

    m2 = df_1['matches'].apply(lambda x: ','.join([i[0] for i in x if i[1] >= threshold]))
    df_1['matches'] = m2
    
    m3 = pd.DataFrame(columns=['loose_match'])
    m3['loose_match'] = df_2[key2].eq(df_1['matches']).replace([True, False], [1,0])
                                 
    return m3  
    #return df_1

df = fuzzy_merge(df3, df4, 'predicted-university', 'gt-university')
df.to_csv("loose-match.csv", index = None, header=True, encoding = 'utf-8')
print(df)

df7 = pd.read_csv('loose-match.csv', encoding = 'utf-8')
count = df7['loose_match'].value_counts()
print(count)

result = pd.concat([df6,df7], axis = 1, sort = False)
result.to_csv("univ_match.csv", index = None, header=True, encoding = 'utf-8')