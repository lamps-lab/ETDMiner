# -*- coding: utf-8 -*-
"""
Created on Sun Jul 26 03:06:32 2020

@author: jhima
"""

#import os
import bs4
from collections import OrderedDict 


def page_info(link_soup):
	page = link_soup.find('div', class_="ocr_page")
	page = page['title']
	image, bbox, page_no = page.split(";")
	a, b, c, d, page_width, page_height = bbox.split(" ")
	#print(page_width, page_height)
	return page_width, page_height

def parseHOCR(link_soup):
	lines = link_soup.find_all('span', class_="ocr_line")
	bbox_info = OrderedDict()
	for line in lines:
		#print(line['id'])
		words = line.find_all('span', class_="ocrx_word")
		#print(words)
		word_info = {}
		#print(line['id'])
		for word in words:
			#print(word['id'])
			#print(word.getText())
			#print(word['title'])
			target_info = word['title']
			bbox , conf = target_info.split(";")
			bbox, startx, starty, endx, endy = bbox.split(" ")
			b, x_wconf, conf = conf.split(" ")
			word_info["line_id"] = line['id']
			word_info["word_id"] = word['id']
			word_info["startx"] = startx
			word_info["starty"] = starty 
			word_info["endx"] = endx
			word_info["endy"] = endy
			word_info["conf"] = conf
			bbox_info[word.getText()] = word_info
	return bbox_info
#this one is necessary 
def get_abs_centre(bbox_info, page_width, page_height):	
	for key in bbox_info:
		startx = int(bbox_info[key]['startx'])
		endx = int(bbox_info[key]['endx'])
		starty = int(bbox_info[key]['starty'])
		endy = int(bbox_info[key]['endy'])
		centerx = ((endx - startx)/2) + startx
		centery = (endy - starty)/2 + starty
		#print(centerx, centery)
		norm_centerx = centerx / int(page_width)
		norm_centery = centery / int(page_height)
		#print(norm_centerx, norm_centery)
		bbox_info[key]['abs_centerx'] = norm_centerx
		bbox_info[key]['abs_centery'] = norm_centery
	return bbox_info


def next_item(dict, key):
	try:
		x = list(dict)[list(dict.keys()).index(key) + 1]
	except:
		#last key
		x = "-"
	#print(x)
	return x

def prev_item(dict, key):
	#print(list(dict).index(key))
	#print(list(dict).index(key)-1)
	#print(list(dict)[list(dict.keys()).index(key) - 1])
	if list(dict).index(key)-1 < 0:
		x = "-"
	else:
		x = list(dict)[list(dict.keys()).index(key) - 1]
	#print(x)
	return x

def get_rel_centre(bbox_info):
	for key in bbox_info:
		#print(key)
		next_key = next_item(bbox_info, key)
		prev_key = prev_item(bbox_info, key)
		#print(prev_key, key, next_key)
		first_last = False
		if prev_key == "-":
			# First key
			print("In First Key")		
			first_last = True
			abs_centerx = int(bbox_info[key]['abs_centerx'])
			abs_centery = int(bbox_info[key]['abs_centery']) 	
			rel_centerx = 2
			rel_centery = 2
			norm_centerx = rel_centerx / 1
			norm_centery = rel_centery / 1
			#print("ggggggggggggggggggggggggggg")            
		elif next_key == "-":
			#last key
			print("In Last Key")
			first_last = True
			abs_centerx = int(bbox_info[key]['abs_centerx'])
			abs_centery = int(bbox_info[key]['abs_centery']) 
			rel_centerx = 4
			rel_centery = 4
			norm_centerx = rel_centerx / 1
			norm_centery = rel_centery / 1
			#print("iiiiiiiiiiiiiiiiiiiiiiiiiii")  
		print(first_last) 
		if not first_last:
			#every other token
			#print(key)
			print("In every other token======")
			print(prev_key, key, next_key)
			#print(bbox_info[prev_key])
			#print(bbox_info[key])
			#print(bbox_info[next_key])
			abs_centerx_p = float(bbox_info[prev_key]['abs_centerx'])
			abs_centery_p = float(bbox_info[prev_key]['abs_centery'])
			abs_centerx = float(bbox_info[key]['abs_centerx'])
			abs_centery = float(bbox_info[key]['abs_centery']) 
			abs_centerx_n = float(bbox_info[next_key]['abs_centerx'])
			abs_centery_n = float(bbox_info[next_key]['abs_centery'])
			print(prev_key, abs_centerx, abs_centerx_p)
			print(prev_key, abs_centery, abs_centery_p)
			rel_centerx = (abs_centerx - abs_centerx_p) 
			rel_centery = (abs_centery - abs_centery_p)
			print(key, rel_centerx, rel_centery)
			norm_centerx = rel_centerx / (abs_centerx_n - abs_centerx_p)
			norm_centery = rel_centery / (abs_centery_n - abs_centery_p)
		bbox_info[key]['rel_centerx'] = norm_centerx
		bbox_info[key]['rel_centery'] = norm_centery
	return bbox_info

def get_width(bbox_info, page_width):
	for key in bbox_info:
		startx = int(bbox_info[key]['startx'])
		endx = int(bbox_info[key]['endx'])
		width = endx - startx
		norm_width = width / int(page_width)
		#print(norm_width)
		bbox_info[key]['width'] = norm_width
	return bbox_info

if __name__ == "__main__":
	with open( "111.html", "r", encoding="utf-8") as f:
		content = f.read()	
	link_soup = bs4.BeautifulSoup(content, "html.parser")
	page_width, page_height = page_info(link_soup)
	bbox_info = parseHOCR(link_soup)
	bbox_info = get_width(bbox_info, page_width)
	bbox_info = get_abs_centre(bbox_info, page_width, page_height)
	bbox_info =  get_rel_centre(bbox_info)
	print(bbox_info['24,'])
      
        
# 	for x, y in zip(test1,test2):
# 		field = x.getText().strip('\n')
# 		field = field[:-1]
# 		data = y.getText().strip('\n')
# 		fieldnames_data = (field,data)
# 		metadata.append(fieldnames_data)
# 	for item in metadata:
# 		if item[0] == "Title":
# 			title = item[1].lower()
# 	
# 	#print(f"{title}\t{author}\t{advisor}\t{university}\t{degree}\t{program}\t{year}\n")
# 	with open( "metadata_groundtruth.tsv", "a") as f:
# 		f.write(f"{title}\t{author}\t{advisor}\t{university}\t{degree}\t{program}\t{year}\n") #
            
