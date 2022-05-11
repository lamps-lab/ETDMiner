#!/usr/bin/env bash

# Loop through all files ending in ".tif"
for f in tif/*.tif ;

do

# Determine output filename
out=${f%%tif} #remove pdf suffix
out=${out#*/} #remove directory path /**/ prefix

out1=$out"txt" #output filename for text file
out2=$out"html"  #output filename for hocr file


#python code to run
python3 tesseract_ocr_hocr.py --image $f --txt $out1 --hOCR $out2

done

#python code to add dummy tags
python3 dummy_tags.py 