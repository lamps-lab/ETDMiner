# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 18:20:23 2020

@author: Muntabir
"""
import pandas as pd
import glob
import os

def concat(indir=r"C:\Users\Muntabir\nltk_data\corpora\cookbook\data"):
    os.chdir(indir)
    fileList = glob.glob("*.csv")
    dfList=[]
    for filename in fileList:
        print(filename)
        df=pd.read_csv(filename, header = None)
        dfList.append(df)
    concatDf = pd.concat(dfList, axis =0)
    print(concatDf)
    concatDf.to_csv("metadata_author-names.csv",index = None)
    
    