#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
Created on Sun 28th Jun
@author: Himarsha Jayanetti
"""

#This code is used to process the y_pred values to obtain each field value by merging tokens.
#Input to the code is the crf model output and the output of this code is fed into the compare_pr_mg.py

def read_csv():
	word_bio_list = []
	with open("test-out.csv", "r") as f:
		word_bio = f.readlines()
	for each in word_bio:
		each = each.strip("\n")
		word, bio = each.split(",")
		word = word.strip("\"")
		bio = bio.strip("\"")
		word_bio_tuple = (word,bio)
		word_bio_list.append(word_bio_tuple)
	#print(word_bio_list)
	return word_bio_list


def collapse(ner_result):
	# List with the result
	collapsed_result = []
	# Buffer for tokens belonging to the most recent entity
	current_entity_tokens = []
	current_entity = "title"
	# Iterate over the tagged tokens
	for token, tag in ner_result:
		#print(current_entity)
		#tag 
		if tag == "O":
			continue
		# If an enitity span starts ...
		#print(token)
		if tag.startswith("B-"):
			# ... if we have a previous entity in the buffer, store it in the result list
			#print("A")
			if current_entity is not None:
				collapsed_result.append(
					(" ".join(current_entity_tokens), current_entity))
			#print("B")
			current_entity = tag[2:]
			#print(current_entity)
			# The new entity has so far only one token
			current_entity_tokens = [token]
		# If the entity continues ..
		elif tag == "I-" + current_entity:
			# Just add the token buffer
			current_entity_tokens.append(token)
			#print(current_entity_tokens)
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
	#print(res)
	res.pop(0)
	res.pop(0) #CHECK WITH ALL CASES IF THIS IS NEEDED
	print(res)
	fields = {} 
	with open ("predicted_results.csv", "w") as g:
		#etdid	title	author	advisor	year	university	degree	program
		g.write("etdid,title,author,advisor,university,degree,program,year\n")
		for doc in res:
			for field in doc:
				fields[field[1]] = field[0]
			#print(fields)
			try:
				title = fields["title"]
			except Exception as e:
				title = ""
			try:
				author = fields["author"]
			except Exception as e:
				author = ""
			try:
				university = fields["university"]
			except Exception as e:
				university =  ""
			try:
				year = fields["year"]
			except Exception as e:
				year =  ""
			try:
				program = fields["program"]
			except Exception as e:
				program =  ""
			try:
				degree = fields["degree"]
			except Exception as e:
				degree =  ""
			try:
				advisor = fields["advisor"]
			except Exception as e:
				advisor =  ""
			#print(title,author,advisor,university,degree,program,year)
			g.write("etdid,%s,%s,%s,%s,%s,%s,%s\n" % (title,author,advisor,university,degree,program,year))


if __name__ == "__main__":
	word_bio_list = read_csv()
	result = collapse(word_bio_list)
	#print(result)
	combine(result)