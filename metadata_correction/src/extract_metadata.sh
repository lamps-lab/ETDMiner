#!/usr/bin/env bash

#title         	:extract_metadata.sh
#description  	:This script takes PDFs ETD as input and output a CSV file containing their Metadata
#author			:Himarsha R. Jayanetti 
#date         	:Saturday, May 21, 2022
#===================================================================================================


#==========
#PDF to TIF
#==========

#Loop through all files ending in ".pdf"
echo "Looping through all ETD PDFs to obtain the cover page ..."
for f in etdrepo/**/**/*.pdf ;

do

# Determine output filename
out1=${f%%pdf} #remove pdf suffix
out2=${out1##*/} #remove directory path /**/ prefix
out="tif/${out2}tif" #output directory and filename

# Ghostscript command to extract coverpage from PDF into TIF format image
# Note: The coverpage is assumed to be the first page. If necessary, modify the page number.
gs -q -sDEVICE=tiffg4 -r300 -dBATCH -dPDFFitPage -dNOPAUSE -dFirstPage=1 -dLastPage=1 -sOutputFile="$out" "$f"

done
echo "Done."
echo " "

#==========
#TIF to TXT
#==========

# Loop through all files ending in ".tif"
echo "Looping through all TIF to extract the text and hOCR output from the TIF images ..."
for f in tif/*.tif ;

do

# Determine output filename
out=${f%%tif} #remove pdf suffix
out=${out#*/} #remove directory path /**/ prefix

out1=$out"txt" #output filename for text file
out2=$out"html"  #output filename for hocr file

#python code to run which would extract the text and hOCR output from the TIF images
python3 tesseract_ocr_hocr.py --image $f --txt $out1 --hOCR $out2

done
echo "Done."
echo " "

#==========
#TXT to XML
#==========


#python code to add dummy tags into the extracted text
#this will create the XML files for each text file in the xml folder
echo "Generating the XML files ..."
python3 dummy_tags.py 

echo "Done."
echo " "

#=========
#CRF Model 
#=========

#Using the saved CRF model to predict the metadata fields
#Provide the path to the saved CRF model pickle file as the first argument
echo "Predicting metadata using the CRF model ..."
python3 crf-test.py crf_model.sav 
#This will output an intermediate file at CRF_output/intermediate.csv

echo "Done."
echo " "

#=============================
#Combine Output & Generate CSV 
#=============================

python3 process_crf_result.py

#This will output the final CSV output file at CRF_output/metadata.csv containing the extracted metadata 


