#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 14:14:26 2020

@author: muntabir
"""

#from pytesseract import pytesseract
#
#path = '/Users/muntabir/Documents/etdExtraction/etd_crf_result/text-align/Tiff/10.tif'
#
#
#pytesseract.run_tesseract(path,"10",extension='tif', lang='eng', config="--psm 4 -c tessedit_create_hocr=1")

import bs4
import glob
import re

noisy_hocr = '/Users/muntabir/Documents/etdExtraction/etd_crf_result/text-align/hocr/1.html'

numbers = re.compile(r'(\d+)')
def numericalSort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts

hocr_files = sorted(glob.glob(noisy_hocr), key=numericalSort)

def hocr_parser():
    for files in hocr_files:
        with open(files, 'r', encoding = "utf-8") as html_input:
            soup = bs4.BeautifulSoup(html_input,'lxml')
            ocr_lines = soup.findAll("span", {"class": "ocrx_word"})
            lines_structure = []
            for line in ocr_lines:
                line_text = line.text.replace("\n"," ")
                title = line['title']
                #The coordinates of the bounding box
                x1,y1,x2,y2 = map(int, title[5:title.find(";")].split())
                lines_structure.append({"x1":x1,"y1":y1,"x2":x2,"y2":y2,"text": line_text})
            
            return lines_structure


parser = hocr_parser()
#print(parser)

for l in parser:
    list_ = []
    tokens = l['text']
    position = l['x1']
    list_.append((tokens, position))
    
    