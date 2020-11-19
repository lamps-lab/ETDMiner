#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 12:39:03 2020

@author: Muntabir Choudhury
"""
import pandas as pd

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



word_bio_list = read_csv()


def collapse(ner_result):
    # List with the result
    collapsed_result = []
    # Buffer for tokens belonging to the most recent entity
    current_entity_tokens = []
    current_entity = ""
    # Iterate over the tagged tokens
    for token, tag in ner_result:
        if tag == "O":
            continue
        # If an enitity span starts ...
        if tag.startswith("B-advisor"):
            # ... if we have a previous entity in the buffer, store it in the result list
            if current_entity is not None:
                collapsed_result.append(
                    (" ".join(current_entity_tokens), current_entity))
                #print(collapsed_result)
                
            current_entity = tag[2:]
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

result = collapse(word_bio_list)
df = pd.DataFrame(result)
df.to_csv("advisor_combined.csv", index = None, encoding = "utf-8")

df1 = pd.read_csv("advisor_combined.csv", encoding='utf-8')
del df1['1']
df1.dropna(inplace=True)
df1.to_csv("7-pradvisor.csv", index=None, header=None, encoding='utf-8')




# for token, tag in word_bio_list:
#     if tag == "O":
#         continue
#     # If an enitity span starts ...
#     if tag.startswith("B-advisor"):
#         # ... if we have a previous entity in the buffer, store it in the result list
#         if current_entity is None:
#             collapsed_result.append(
#                 (" ".join(current_entity_tokens), current_entity))
        
#         current_entity = tag[2:]
#         #print(current_entity)
#         # The new entity has so far only one token
#         current_entity_tokens = [token]
#         #print(current_entity_tokens)

#     elif tag == "I-" + current_entity:
#         # Just add the token buffer
#         current_entity_tokens.append(token)
#         #print(current_entity_tokens)

# if current_entity is not None:
#     collapsed_result.append(
#         (" ".join(current_entity_tokens), current_entity))
#     print(collapsed_result)
#     #df = pd.DataFrame(collapsed_result, columns=['advisor', 'tag'])
#     #df.to_csv("advisor_combined.csv", encoding = "utf-8")

