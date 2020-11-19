#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
Created on Sun 28th Jun
@author: Himarsha Jayanetti
"""

#This code is used to process the y_pred values to obtain each field value by merging tokens.
#Input to the code is the crf model output and the output of this code is fed into the compare_pr_mg.py

def read_tsv():
	word_bio_list = []
	with open("test-out.csv", "r") as f:
		word_bio = f.readlines()
	for each in word_bio:
		each = each.strip("\n")
		word, bio = each.split(",")
		word_bio_tuple = (word,bio)
		word_bio_list.append(word_bio_tuple)
	#print(word_bio_list)
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
                
            current_entity = tag[2:]
            # The new entity has so far only one token
            current_entity_tokens = [token]
		# If the entity continues ...
        elif tag == "I-" + current_entity:
            # Just add the token buffer
            current_entity_tokens.append(token)
            print(current_entity_tokens)
        else:
            raise ValueError("Invalid tag order.")
    
    # The last entity is still in the buffer, so add it to the result
	# ... but only if there were some entity at all
    if current_entity is not None:
        collapsed_result.append(
            (" ".join(current_entity_tokens), current_entity))
	#print(collapsed_result)
    return collapsed_result

def combine(field_list):
    size = len(field_list)
    idx_list = [idx  for idx, val in enumerate(field_list) if val[1] == "title"]
    res = [field_list[i: j] for i, j in zip([0] + idx_list, idx_list + ([size] if idx_list[-1] != size else []))]
    res.pop(0)
	#print(res)
	#print(res[0])
	#print(res[1])
	#docs = {}
    fields = {}
    for doc in res:
        for field in doc:
            fields[field[1]] = field[0]
        title = fields["title"]
        author = fields["author"]
        university = fields["university"]
        #year = fields["year"]
        program = fields["program"]
        degree = fields["degree"]
# 		with open ("predicted_results.tsv", "a") as g:
#  			g.write("%s\t%s\t%s\t%s\t%s\t%s\n" % (title,author,university,degree,program,year))
        with  open ("pr_title.csv", "a") as g1:
            g1.write("%s\n" % title)
        with open ("pr_author.csv", "a") as g2:
            g2.write("%s\n" % author)
        with open ("pr_program.csv", "a") as g3:
            g3.write("%s\n" % program)
        # with open ("pr_year.csv", "a") as g4:
        #     g4.write("%s\n" 
        with open ("pr_univ.csv", "a") as g5:
            g5.write("%s\n" % university)
        with open ("pr_degree.csv", "a") as g6:
            g6.write("%s\n" % degree)
		#with open ("pr_advisor.csv", "a") as g7:
		#	g7.write("%s\n" % advisor)
	#doc_list.append(fields)
	#print(doc_list[0])
	#print(doc_list[1])

if __name__ == "__main__":
    word_bio_list = read_tsv()
    result = collapse(word_bio_list)
    #print(result)
    combine(result)