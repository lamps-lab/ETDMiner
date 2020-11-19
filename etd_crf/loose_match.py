import os, os.path
import sys
import glob
import re
import csv
import pandas as pd
from fuzzywuzzy import fuzz

output_file = "program.csv"
output_file1 = output_file.strip(".csv") + "1.csv"
#print(output_file1)
#Loose matching
with open (output_file, "r", encoding = "latin1") as f:
    content = f.readlines()
    content.pop(0)
    with open(output_file1, "w") as g:
        g.write(",crf_out,metadata,ratio,match,loose_match\n")    
    l_match = ["Loose_match"]
    for line in content:
        n,title1, title2, val1 = line.split(",")
        #print(title1)
        #print(title2)        
        Ratio = fuzz.ratio(title1,title2)
        PRatio = fuzz.partial_ratio(title1,title2)
        #print(Ratio, PRatio)
        if Ratio >= 60:
            val2 = 1
        else:
            val2 = 0
        print(n, title1, title2, Ratio)
        l_match.append(val2)
        with open(output_file1, "a") as g:
            string = f"{n},{title1},{title2},{Ratio},{val1[:-1]},{val2}\n"
            #print(string)
            g.write(string)


    
        
        
    