#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  2 16:57:36 2022

@author: muntabir
"""
import pandas as pd

etd_space = pd.read_csv("etd_space100.csv")
etd_space.columns = ['etd_space_id']
etd_space.sort_values('etd_space_id', ascending=True, inplace=True, ignore_index=True)
etd_space.to_csv("etd_space100_updated.csv", index = None)

year_space = pd.read_csv("year_space100.csv")
year_space.columns = ['year_space_id']
year_space.sort_values('year_space_id', ascending=True, inplace=True, ignore_index=True)
year_space.to_csv("year_space100_updated.csv", index = None)

uni_space = pd.read_csv("university_space100.csv")
uni_space.columns = ['uni_space_id']
uni_space.sort_values('uni_space_id', ascending=True, inplace=True, ignore_index=True)
uni_space.to_csv("uni_space100_updated.csv", index = None)

df1 = pd.read_csv("etd_space100_updated.csv")
df2 = pd.read_csv("year_space100_updated.csv")
df3 = pd.read_csv("uni_space100_updated.csv")

result = pd.concat([df1, df2, df3], axis = 1, sort = False)
result.to_csv("etdSpaceIDs.csv", index = None)