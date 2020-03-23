# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 18:20:23 2020

@author: Muntabir
"""
import pandas as pd
import glob
import re

path=r"C:\Users\Muntabir\nltk_data\corpora\cookbook\degree_metadata\*.csv"
numbers = re.compile(r'(\d+)')
def numericalSort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts

fileList = sorted(glob.glob(path),  key=numericalSort)
dfList=[]
colname=['degree']

for filename in fileList:
    print(filename)
    df=pd.read_csv(filename, header = None)
    dfList.append(df)

concatDf = pd.concat(dfList, axis =0)
concatDf.columns=colname
concatDf.to_csv("metadata_degree.csv",index = None)

