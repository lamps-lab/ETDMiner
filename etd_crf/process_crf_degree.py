#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  2 00:38:21 2020

@author: muntabir choudhury
"""


def read_csv():
    word_bio_list = []
    with open("test-out-150.csv", "r") as f:
        word_bio = f.readlines()
        word_bio = word_bio
    for each in word_bio:
        each = each.strip("\n").strip(',')
        word, bio = each.split(",")
        #print(word,bio)
        word_bio_tuple = (word,bio)
        word_bio_list.append(word_bio_tuple)
    return word_bio_list


def collapse(ner_result):
    b_tokens = ""
    i_tokens = ""
    for token, tag in ner_result:
        if tag == "B-degree": 
            b_tokens = [token]
            #print(b_tokens)
        
        elif tag == "I-degree":
            tag_list = []
            each_row = token.split("\n")
            print(each_row)
            #i_tokens = b_tokens + " " + token
        
        #print(i_tokens)
        
        
        
        

        
if __name__ == "__main__":
    word_bio_list = read_csv()
    result = collapse(word_bio_list)
    #print(result)
    #combine = combine(result)    