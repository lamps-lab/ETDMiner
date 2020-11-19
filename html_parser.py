#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
Created on Tue 2nd Jun
@author: Himarsha Jayanetti
"""

#This parser can be used to download metadata from ProQuest Dissertations & Theses Global.
#Use this code to parse the html of Details/Abstract section for any ETD in the database

import os
import bs4

def parseMetadata(html):
	link_soup = bs4.BeautifulSoup(html, "html.parser" )
	test1 = link_soup.find_all('div', class_="display_record_indexing_fieldname")
	test2 = link_soup.find_all('div', class_="display_record_indexing_data")
	metadata = []
	#print(test1)
	for x, y in zip(test1,test2):
		field = x.getText().strip('\n')
		field = field[:-1]
		data = y.getText().strip('\n')
		fieldnames_data = (field,data)
		metadata.append(fieldnames_data)
	for item in metadata:
		if item[0] == "Title":
			title = item[1].lower()			
		if item[0] == "Subject":
				program = item[1].lower()	
		if item[0] == "Author":
			author = item[1].lower()	
		if item[0] == "Publication year":
			year = item[1].lower()	
		if item[0] == "University/institution":
			university = item[1].lower()	
		if item[0] == "Degree":
			degree = item[1].lower()	
	with open( "metadata_groundtruth.tsv", "a") as f:
		f.write(f"{title}\t{author}\t{university}\t{degree}\t{program}\t{year}\n") #advisor
	with open("mg_title.csv", "a") as g1:
		g1.write(f"{title}\n")
	with open("mg_author.csv", "a") as g2:
		g2.write(f"{author}\n")
	with open("mg_univ.csv", "a") as g3:
		g3.write(f"{university}\n")
	with open("mg_degree.csv", "a") as g4:
		g4.write(f"{degree}\n")
	with open("mg_program.csv", "a") as g5:
		g5.write(f"{program}\n")
	with open("mg_year.csv", "a") as g6:
		g6.write(f"{year}\n")
	#with open("mg_advisor.csv", "a") as g6:
	#	g6.write(f"{advisor}\n")


if __name__ == "__main__":
	with open( "metadata_groundtruth.tsv", "a") as f:
		f.write(f"title\tauthor\tuniversity\tdegree\tprogram\tyear\n")
	for i in range(101,111):
		try:
			html_file = "html_files/%s.html" %i
			with open(html_file, "r") as f:
				content = f.read()
				try:
					parseMetadata(content)
				except:
					print("Error in:" + str(i))
					pass	
		except:
			pass

