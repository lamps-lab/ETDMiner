#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 03:30:54 2020

@author: Muntabir Choudhury
"""


import pandas as pd

dfList=[]
colname=['predicted-program']
df1 = pd.read_csv("3-prprogram.csv", encoding='utf-8', header=None)
dfList.append(df1)
concatDf = pd.concat(dfList, axis =0)
concatDf.columns=colname
concatDf.to_csv('pr_program.csv', index = None, header=True, encoding = 'utf-8') #actual predicted title with header

dfList1=[]
colname=['gt-program']
df2 = pd.read_csv("program_gt.csv", encoding ='utf-8', header=None)
dfList1.append(df2)
concatDf = pd.concat(dfList1, axis =0)
concatDf.columns=colname
concatDf.to_csv('gt_program.csv', index = None, header=True, encoding = 'utf-8') #actual ground truth title with header

# # print(df1)
# # print(df2)
dfList1=[]
colname=['visual-program']
df3 = pd.read_csv("visual-program_gt.csv", encoding ='utf-8', header=None)
dfList1.append(df3)
concatDf = pd.concat(dfList1, axis =0)
concatDf.columns=colname
concatDf.to_csv('gt_visual-program.csv', index = None, header=True, encoding = 'utf-8')

df4 = pd.read_csv('pr_program.csv', encoding='utf-8')
df5 = pd.read_csv('gt_program.csv', encoding='utf-8')
df6 = pd.read_csv('gt_visual-program.csv', encoding='utf-8')


df7 = pd.DataFrame(columns=['match'])
df7['match'] = df4['predicted-program'].eq(df5['gt-program']).replace([True, False], [1,0])
result = pd.concat([df4, df5, df6, df7], axis = 1, sort = False)
result.to_csv('program_gt-match.csv', index = None, header=True, encoding = 'utf-8') #contains the binary match between predicted title and ground truth title

df8 = pd.read_csv("program_gt-match.csv", encoding = 'utf-8')

df9 = pd.DataFrame(columns=['visual-match'])
df9['visual-match'] = df8['predicted-program'].eq(df8['visual-program']).replace([True, False], [1,0])
result = pd.concat([df8, df9], axis = 1, sort = False)
result.to_csv('program_outfile.csv', index = None, header=True, encoding = 'utf-8')

df10 = pd.read_csv('program_outfile.csv', encoding = 'utf-8')
count1 = df10['match'].value_counts()
count2 = df10['visual-match'].value_counts()
print(count1)
print(count2)