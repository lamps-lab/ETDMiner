#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
Created on Sun 28th Jun 2021
@author: Himarsha Jayanetti

Modified on: 
By:  Himarsha Jayanetti
"""

from collections import defaultdict


#This code is used to process the y_pred values to obtain each field value by merging tokens.
#Input to the code is the crf model output and the output of this code is fed into the compare_pr_mg.py

def read_csv():
	with open("CRF_output/intermediate.csv", "r") as f:
		main_list = f.readlines()
	#print(main_list)
	#main_dic = {}
	main_dic = defaultdict(list)
	word_bio_list = []
	for each in main_list:
		each = each.strip("\n")
		etdid, word, bio = each.split(",")
		word = word.strip("\"")
		bio = bio.strip("\"")
		word_bio_tuple = (etdid,word,bio)
		word_bio_list.append(word_bio_tuple)
	for k, *v in word_bio_list:
		main_dic[k].append(v)
	#print(main_dic["2000"])
	return main_dic


def collapse(ner_result):
	# List with the result
	collapsed_result = []
	# Buffer for tokens belonging to the most recent entity
	current_entity_tokens = []
	current_entity = "title"
	# Iterate over the tagged tokens
	for token, tag in ner_result:
		#print(current_entity)
		#print(token,tag) 
		# if newID:
		# 	current_entity = "title"
		# 	newID = False
		if tag == "O":
			continue
		# If an enitity span starts ...
		#print(token)
		if tag.startswith("B-"):
			#print("HERE - B")
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
			#print(tag)
			#print("HERE - I")
			# Just add the token buffer
			current_entity_tokens.append(token)
			#print(current_entity_tokens)
		else:
			#print(token,tag)
			raise ValueError("Invalid tag order.")
		# prev_etdid = etdid
		#print("END")
		#break
		#print(collapsed_result)
	
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
	#res.pop(0) #USE IF NEEDED
	#print(res)
	fields = {} 
	#etdid	title	author	advisor	year	university	degree	program
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
		out_line = "%s,%s,%s,%s,%s,%s,%s\n" % (title.strip("\n"),author.strip("\n"),advisor.strip("\n"),university.strip("\n"),degree.strip("\n"),program.strip("\n"),year.strip("\n"))
		#break
		#print(out_line)
	return out_line

if __name__ == "__main__":	
	main_dic = read_csv()

	with open ("CRF_output/metadata.csv", "w") as g:		
		g.write("etdid,title,author,advisor,university,degree,program,year\n")
		for key in main_dic.keys():
			#print(key)
			#print(main_dic[key])
			word_bio =main_dic[key]
			result = collapse(word_bio)
			out_line = combine(result)
			g.write(key + "," + out_line)
			#break
