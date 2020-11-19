import os, os.path
import sys
import glob
import re
import csv
import pandas as pd
from fuzzywuzzy import fuzz

output_file = "author.csv"
output_file1 = output_file.strip(".csv") + "1.csv"
#print(output_file1)
#Loose matching
with open (output_file, "r", encoding = "latin1") as f:
    content = f.readlines()
    content.pop(0)
    with open(output_file1, "w") as g:
        g.write(",first_name1,last_name1,first_name2,last_name2,first_name_status,first_name_status_loose,last_name_status,last_name_status_loose,match,loose_match\n")    
    #l_match = ["Loose_match"]
    for line in content:
        n,fname1,mname1,lname1,fname2,mname2,lname2,fmatch,mmatch,lmatch,match = line.split(",")
        #print(title1)
        #print(title2)        
        Ratio1 = fuzz.ratio(fname1,fname2)
        Ratio2 = fuzz.ratio(lname1,lname2)
        #PRatio = fuzz.partial_ratio(title1,title2)
        #print(Ratio, PRatio)
        if Ratio1 >= 60:
            val1 = 1
        else:
            val1 = 0
        if Ratio2 >= 60:
            val2 = 1
        else:
            val2 = 0
        if val1 == 1 and val2 == 1:
            val3 = 1
        else:
            val3 = 0    
        #print(n, title1, Ratio)
        #l_match.append(val2)
        with open(output_file1, "a") as g:
            string = f"{n},{fname1},{lname1},{fname2},{lname2},{fmatch},{val1},{lmatch},{val2},{match[:-1]},{val3}\n"
            #string = f"{n},{title1},{title2},{val1[:-1]},{val2}\n"
            print(string)
            g.write(string)