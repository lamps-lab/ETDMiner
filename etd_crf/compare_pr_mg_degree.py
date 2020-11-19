#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  2 00:16:48 2020

@author: Muntabir Choudhury
"""


import pandas as pd
import csv

dfList=[]
colname=['predicted-degree']
df1 = pd.read_csv("6-prdegree.csv", encoding='utf-8', header=None)
dfList.append(df1)
concatDf = pd.concat(dfList, axis =0)
concatDf.columns=colname
concatDf.to_csv('pr_degree.csv', index = None, header=True, encoding = 'utf-8') #actual predicted title with header

df2 = pd.read_csv("pr_degree.csv", encoding = 'utf-8')
#print(df2)

f1 = open("degree_appendix.csv", 'r', encoding = "ISO-8859-1")
reader = csv.reader(f1)

#reading the degree appendix file as a dictionary
def dict_degree():
    degree_appendix = {}
    for row in reader:
        degree_appendix[row[0]] = row[1]
    return degree_appendix

dict_check = dict_degree()
#print(dict_check)

#mapping a dictionary to a dataframe
df2['predicted-degree'] = df2['predicted-degree'].map(dict_check)
df2.to_csv("pr_degree-mapped.csv", index = None)


dfList=[]
colname=['gt-degree']
df3 = pd.read_csv("degree_gt.csv", encoding='utf-8', header=None)
dfList.append(df3)
concatDf = pd.concat(dfList, axis =0)
concatDf.columns=colname
concatDf.to_csv('gt_degree.csv', index = None, header=True, encoding = 'utf-8')


df4 = pd.read_csv("pr_degree-mapped.csv", encoding = 'utf-8')
df5 = pd.read_csv("gt_degree.csv", encoding = "utf-8")

df6 = pd.DataFrame(columns=['crf_match'])
df6['crf_match'] = df4['predicted-degree'].eq(df5['gt-degree']).replace([True, False], [1,0])
result = pd.concat([df4, df5, df6], axis = 1, sort = False)
result.to_csv('degree_outfile.csv', index = None, header=True, encoding = 'utf-8') #contains the binary match between predicted title and ground truth title

df7 = pd.read_csv('degree_outfile.csv', encoding = 'utf-8')
count = df6['crf_match'].value_counts()
print(count)