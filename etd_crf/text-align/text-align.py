#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  7 18:37:26 2021

@author: Muntabir Choudhury
"""


#import libraries
import edlib
import glob
import re

clean = '/Users/muntabir/Documents/text-align_data/clean/4.txt'
noisy = '/Users/muntabir/Documents/text-align_data/noisy/4.txt'

numbers = re.compile(r'(\d+)')
def numericalSort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts


target_files = sorted(glob.glob(clean), key=numericalSort)
query_files = sorted(glob.glob(noisy), key=numericalSort)

def query():
    for files in query_files:
        with open(files, mode='r') as query:
            texts = []
            for lines in query:
                text = lines
                texts.append(text)
            return texts

def target():
    for files in target_files:
        with open(files, mode='r') as target:
            texts = []
            for lines in target:
                texts.append(lines)   
            
            return texts
        
def listToString(text):
        _string = ""
        return(_string.join(text))

query_text = query()
query_ = listToString(query_text)
target_text = target()
target_ = listToString(target_text)
result = edlib.align(query_, target_, task="path")

alignment = edlib.getNiceAlignment(result, query_, target_)
#print("\n".join(alignment.values()))
print(alignment['target_aligned'])
#import re
#
#import edlib
#
#
#def edlib2pair(query: str, ref: str, mode: str = "NW") -> str:
#    """
#    input:
#    query and ref sequence
#
#    output:
#    TAAGGATGGTCCCAT TC
#     ||||  ||||.||| ||
#     AAGG  GGTCTCATATC
#    """
#
#    a = edlib.align(query, ref, mode=mode, task="path")
#    ref_pos = a["locations"][0][0]
#    query_pos = 0
#    ref_aln = match_aln = query_aln = ""
#
#    for step, code in re.findall("(\d+)(\D)", a["cigar"]):
#        step = int(step)
#        if code == "=":
#            ref_aln += ref[ref_pos : ref_pos + step]
#            ref_pos += step
#            query_aln += query[query_pos : query_pos + step]
#            query_pos += step
#            match_aln += "|" * step
#        elif code == "X":
#            ref_aln += ref[ref_pos : ref_pos + step]
#            ref_pos += step
#            query_aln += query[query_pos : query_pos + step]
#            query_pos += step
#            match_aln += "." * step
#        elif code == "D":
#            ref_aln += ref[ref_pos : ref_pos + step]
#            ref_pos += step
#            query_aln += " " * step
#            query_pos += 0
#            match_aln += " " * step
#        elif code == "I":
#            ref_aln += " " * step
#            ref_pos += 0
#            query_aln += query[query_pos : query_pos + step]
#            query_pos += step
#            match_aln += " " * step
#        else:
#            pass
#
#    return f"{ref_aln}\n{match_aln}\n{query_aln}"
#
#
#if __name__ == "__main__":
#    REF = "TAAGGATGGTCCCATTC"
#    QUERY = "AAGGGGTCTCATATC"
#    PAIR = edlib2pair(QUERY, REF, mode="NW")
#    print(PAIR)