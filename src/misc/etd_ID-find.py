#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 21 19:03:23 2022

@author: muntabir
"""


import pandas as pd
import numpy as np

etd500_title = pd.read_csv('/Users/muntabir/Documents/metadataImprovement/title_metadata.csv')

etdDB_title = pd.read_csv('/Users/muntabir/Documents/metadataImprovement/etddb_title.csv')

etdDB = etdDB_title['title'].str.strip().str.lower()
etd500 = etd500_title['title'].str.strip()

#df = etdDB.to_frame().merge(etd500.to_frame(), how = 'inner', indicator = False)

df = pd.DataFrame(columns=['match'])
df['match'] = pd.Series([m.all() for m in np.isin(etdDB.values,etd500.values)])

result = pd.concat([etdDB_title, df], axis = 1, sort = False)
result.to_csv('etdmatch.csv', index = None, header=True, encoding = 'utf-8')

ETD_data = pd.read_csv('etdmatch.csv')
ETD_id = ETD_data[ETD_data['match'] == True]
ETD_id.to_csv('ETD_id.csv', index = None, header=True, encoding = 'utf-8')