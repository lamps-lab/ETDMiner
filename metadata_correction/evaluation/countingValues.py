#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  2 16:57:36 2022

@author: muntabir
"""
import pandas as pd

metadata_raw = pd.read_csv("etd_records.csv")
metadata_updated = pd.read_csv("etd_records_v3.csv")

print("#### Missing Values (percent) of Seven Metadata Fields ####")
title = metadata_raw['title'].isna().sum()
print(f"Title: {(title / 300) * 100}")
author = metadata_raw['author'].isna().sum()
print(f"Author: {(author / 300) * 100}")
university = metadata_raw['university'].isna().sum()
print(f"University: {(university / 300) * 100}")
degree = metadata_raw['degree'].isna().sum()
print(f"Degree: {(degree / 300) * 100}")
year = metadata_raw['year'].isna().sum()
print(f"Year: {(year / 300) * 100}")
advisor = metadata_raw['advisor'].isna().sum()
print(f"Advisor: {(advisor / 300) * 100}")
department = metadata_raw['department'].isna().sum()
print(f"Department: {(department / 300) * 100}")


print("\n")
print("#### Missing Values (percent) updated using AutoMeta ####")

title = metadata_updated['title'].isna().sum()
print(f"Title: {(title / 300) * 100}")
author = metadata_updated['author'].isna().sum()
print(f"Author: {(author / 300) * 100}")
university = metadata_raw['university'].isna().sum()
print(f"University: {(university / 300) * 100}")
degree = metadata_updated['degree'].isna().sum()
print(f"Degree: {(degree / 300) * 100}")
year = metadata_updated['year'].isna().sum()
print(f"Year: {(year / 300) * 100}")
advisor = metadata_updated['advisor'].isna().sum()
print(f"Advisor: {(advisor / 300) * 100}")
department = metadata_updated['department'].isna().sum()
print(f"Department: {(department / 300) * 100}")