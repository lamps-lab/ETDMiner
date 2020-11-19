#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 04:30:11 2020

@author: muntabir
"""


import pandas as pd


dfList=[]
colname=['predicted-year']
df1 = pd.read_csv("pryear.csv", encoding='utf-8', header=None)
dfList.append(df1)
concatDf = pd.concat(dfList, axis =0)
concatDf.columns=colname
concatDf.update(concatDf[['predicted-year']].applymap('"{}"'.format)) #making it string by applying quotation
concatDf.to_csv('pr_year.csv', index = None, header=True, encoding = 'utf-8') #actual predicted title with header


dfList1=[]
colname=['gt-year']
df2 = pd.read_csv("year_gt.csv", encoding ='utf-8', header=None)
dfList1.append(df2)
concatDf = pd.concat(dfList1, axis =0)
concatDf.columns=colname
concatDf.update(concatDf[['gt-year']].applymap('"{}"'.format)) #making it string by applying quotation
concatDf.to_csv('gt_year.csv', index = None, header=True, encoding = 'utf-8') #actual ground truth title with header

#print(df1)
#print(df2)

df3 = pd.read_csv('pr_year.csv', encoding='utf-8')
print(df3)
df4 = pd.read_csv('gt_year.csv', encoding='utf-8')
print(df4)


df5 = pd.DataFrame(columns=['match'])
df5['match'] = df3['predicted-year'].eq(df4['gt-year']).replace([True, False], [1,0])
result = pd.concat([df3, df4, df5], axis = 1, sort = False)
result.to_csv('year_outfile.csv', index = None, header=True, encoding = 'utf-8') #contains the binary match between predicted title and ground truth title

df6 = pd.read_csv('year_outfile.csv', encoding = 'utf-8')
count = df6['match'].value_counts()
print(count)