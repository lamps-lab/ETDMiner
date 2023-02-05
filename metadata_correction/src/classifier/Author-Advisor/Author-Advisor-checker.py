"""
This script will check Author and Advisor names to detect error

"""
import json
import os
import mysql.connector
from bs4 import BeautifulSoup
from shutil import copyfile
import xml.etree.ElementTree as ET
import urllib.request
import urllib.response
import urllib.parse
import re
import time
import ssl
from socket import timeout
import pandas as pd
from flair.data import Sentence
from flair.models import SequenceTagger
import numpy as np


def find_entity(text):
    tagger = SequenceTagger.load("flair/ner-english-ontonotes-large")
    sentence = Sentence(text)
    tagger.predict(sentence)
    for entity in sentence.get_spans('ner'):
        entity_label = entity.get_label("ner").value
        if(entity_label == 'PERSON'):
            return 1
        else:
            return 0
            

dataset = pd.read_csv('Author-Advisor500.CSV') // TODO; It takes a CSV file as input which has 3 coulmns (ETDID, AUTHOR, ADVISOR)
etds = pd.DataFrame(dataset)


author = []
advisor=[]
etdid = []


for index, row in etds.iterrows():
    etd_id = row[0]
    author_name = row[1]
    advisor_name= row[2]
    print("author:", row[2])
    #field values
    try:
        author_name = author_name.split(',')[0]+author_name.split(',')[1]
    except:
        author_name=""
    try:
        advisor_name = advisor_name.split(',')[0]+advisor_name.split(',')[1]
    except:
        advisor_name=""
    
    
    # calls FlairNLP to check Author and Advisor names
    try:
        etdid.append(etd_id)
        author.append(find_entity(str(author_name)))
        advisor.append(find_entity(str(advisor_name)))
        print("Author",author_name)
    except:
        pass
    
    etdid.append(row[0])
    
    

etd_dataframe = pd.DataFrame (etdid, columns = ['etd_id'])
author_dataframe = pd.DataFrame (author, columns = ['author'])
adviso = pd.DataFrame (advisor, columns = ['advisor'])
dataframe = pd.concat([df, df2, df3],axis=1)

# Generates a CSV file with 3 coulmns (etd_id, author, advisor). The author and advisor column has two types of values: 0 or 1. 1 = correct and 0 = incorrect
dataframe.to_csv('Anomaly_detected.csv', header=['etd_id','author','advisor'], index=False)
