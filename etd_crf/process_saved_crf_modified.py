#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  8 22:54:32 2020

@author: muntabir choudhury

(updated) -- made current_entity = 'title'
"""


#This code is used to process the y_pred values to obtain each field value by merging tokens.
#Input to the code is the crf model output and the output of this code is fed into the compare_pr_mg.py
import csv

# csvfile = open('fileds.csv', 'w')
# csv_writer = csv.writer(csvfile)

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
    # List with the result
    collapsed_result = []
    # Buffer for tokens belonging to the most recent entity
    current_entity_tokens = []
    current_entity = None
    # Iterate over the tagged tokens
    for token, tag in ner_result:
        if tag == "O":
            continue
        # If an enitity span starts ...
        if tag.startswith("B-"):
            # ... if we have a previous entity in the buffer, store it in the result list
            if current_entity is not None:
                collapsed_result.append(
                    (" ".join(current_entity_tokens), current_entity))
                #print(collapsed_result)
                
            current_entity = tag[2:]
            #print(current_entity)
            # The new entity has so far only one token
            current_entity_tokens = [token]
            #print(current_entity_tokens)
		 #If the entity continues ...
        elif tag == "I-" + current_entity:
            # Just add the token buffer
            current_entity_tokens.append(token)
            #print(current_entity_tokens)
        # else:
        #     return current_entity_tokens
    
     # The last entity is still in the buffer, so add it to the result
 	 # ... but only if there were some entity at all
    if current_entity is not None:
        collapsed_result.append(
            (" ".join(current_entity_tokens), current_entity))
        #print(collapsed_result)
    return collapsed_result

# def remove_tuples(tuples):
#     tuples = [t for t in tuples if t == None]
#     return tuples


def combine(field_list):
    # for row in field_list:
    #     csv_writer.writerow(row)
        size = len(field_list)
        idx_list = [idx  for idx, val in enumerate(field_list) if val[1] == 'title']
        res = [field_list[i: j] for i, j in zip([0] + idx_list, idx_list + ([size] if idx_list[-1] != size else []))]
        res.pop(0)
        #print(res)
        fields = {}
        for doc in res:
            for field in doc:
                fields[field[1]] = field[0]
            
            title = fields["title"]
            #print(title)
            university = fields["university"]
            #print(university)
            author = fields["author"]
            #print(author)
            year = fields["year"]
            #print(year)
            program = fields["program"]

            degree = fields["degree"]
            #print(degree)
            advisor = fields["advisor"]
            print(advisor)


            # with open ("1-prtitle.csv", "a") as g1:
            #     g1.write("%s\n" % title)
            # with open ("2-prauthor.csv", "a") as g2:
            #     g2.write("%s\n" % author)
            # with open ("3-prprogram.csv", "a") as g3:
            #     g3.write("%s\n" % program)
            # with open ("4-pryear.csv", "a") as g4:
            #     g4.write("%s\n" % year)
            # with open ("5-pruniv.csv", "a") as g5:
            #     g5.write("%s\n" % university)
            # with open ("6-prdegree.csv", "a") as g6:
            #     g6.write("%s\n" % degree)
            # with open("7-pradvisor.csv", "a") as g7:
            #     g7.write("%s\n" % advisor)

if __name__ == "__main__":
    word_bio_list = read_csv()
    result = collapse(word_bio_list)
    combine = combine(result)    