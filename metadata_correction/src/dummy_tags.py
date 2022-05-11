"""
Created on Sun 13 March, 2022
@author: Himarsha Jayanetti
"""

import glob, os
import re

def add_tags(file):
	new_list = []
	try:
		#print(file)
		with open(file, "r") as f:
			 lines = f.readlines()
		#Remove new line character from each element in list
		lines2 = [x.replace('\n', '') for x in lines]
		#print(lines2)
		for line in lines2:
			#Remove invalid characters
			line = re.sub(r'\W+', ' ', line)
			#Ignore elements with "" or " "
			if line == "" or line == " ":
				pass
			else:
				#Add dummy tag - <dt> and </dt>
				line = "<dt>" + line + "</dt>"
				new_list.append(line)
			#new_list.append(line)
		#print(new_list)
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

def add_doctagONLY(file):
	new_list = []
	try:
		#print(file)
		with open(file, "r") as f:
			 lines = f.readlines()
		first_item = lines[0]
		lines[0] = "<document>" + first_item
		last_item = lines[-1]
		lines[-1] = last_item + "</document>" 
		#print(new_list)
	except Exception as e:
		print(f"{file}, Error")
		pass
	return lines


if __name__ == "__main__":
	for file in glob.glob("txt/*.txt"):
		#print(file)
		modified_text = add_doctagONLY(file)
		#print(modified_text)
		new_file = "xml/" + file.strip(".txt") + ".xml"
		with open(new_file,"w") as g:
			g.write("\n".join(modified_text))