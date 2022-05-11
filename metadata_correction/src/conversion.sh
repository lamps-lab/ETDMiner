#!/usr/bin/env bash

# Change to the "pdf" directory to find the input files
# cd 12TestETDs/ || { echo ERROR: Subdirectory 12TestETDs not found; exit 1; }
#12TestETDs/1
#BornDigital, OCR,ScannednotOCR,CompleteDisagreement

# Loop through all files ending in ".pdf"
for f in etdrepo/**/*.pdf ;

do

# Determine output filename
out1=${f%%pdf} #remove pdf suffix
out2=${out1##*/} #remove directory path /**/ prefix
out="tif/${out2}tif" #output directory and filename

# # Show the command we would run
# #gs -q -sDEVICE=tiffg4 -r300 -dBATCH -dPDFFitPage -dNOPAUSE -dFirstPage=2 -dLastPage=2 -sOutputFile="$out" "$f"
gs -q -sDEVICE=tiffg4 -r300 -dBATCH -dPDFFitPage -dNOPAUSE -dFirstPage=1 -dLastPage=1 -sOutputFile="$out" "$f"

done