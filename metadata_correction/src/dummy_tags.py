#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-

#title         	:dummy_tags.py
#description  	:This code takes extracted cover page text files as input and output a XML file. 
#				 This code adds the document root element and remove extra new lines and invalid characters.
#author			:Himarsha R. Jayanetti 
#date         	:Saturday, May 21, 2022
#===================================================================================================

import glob, os
import re

def get_items(file):
	new_list = []
	with open(file, "r") as f:
		lines = f.readlines()
	#Remove new line character from each element in list
	lines = [x.replace('\n', '') for x in lines]
	#Remove invalid characters
	for line in lines:
		line = re.sub(r'[^\w.,;!? \n]+', '', line)
		new_list.append(line)
	return new_list

def add_doctagONLY(item_list):
	new_list = []
	try:
		for line in item_list:
			new_list.append(line)
		first_item = new_list[0]
		new_list[0] = "<document>" + first_item
		last_item = new_list[-1]
		new_list[-1] = last_item + "</document>" 
	except Exception as e:
		print(f"{file}, Error")
		pass
	return new_list


def add_tags(item_list):
	new_list =[]
	try:
		for line in item_list:
			#Ignore elements with "" or " "
			if line == "" or line == " ":
				pass
			else:
				#Add dummy tag - <dt> and </dt>
				line = "<dt>" + line + "</dt>"
			new_list.append(line)
		#Add document root tag - <document> and </document>
		first_item = new_list[0]
		new_list[0] = "<document>" + first_item
		last_item = new_list[-1]
		new_list[-1] = last_item + "</document>" 
		#print(new_list)
	except Exception as e:
		print(f"{file}, Error")
		pass
	return new_list


if __name__ == "__main__":
	for file in glob.glob("txt/*.txt"):
		item_list = get_items(file)
		modified_text = add_doctagONLY(item_list) #This function only adds the document root tags.
		#Call add_tags() fuction if it is required to add dummy tags to each line.
		new_file = "xml/" + file.strip(".txt") + ".xml"
		with open(new_file,"w") as g:
			g.write("\n".join(modified_text))