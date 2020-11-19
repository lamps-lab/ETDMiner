#!/usr/bin/env bash

# Change to the "pdf" directory to find the input files
cd pdf || { echo ERROR: Subdirectory pdf not found; exit 1; }

# Loop through all files ending in ".pdf"
for f in *.pdf;

do

# Determine output filename
out=${f%%pdf}
out="../tif/${out}tif"

# Show the command we would run
gs -q -sDEVICE=tiffg4 -r300 -dBATCH -dPDFFitPage -dNOPAUSE -dFirstPage=1 -dLastPage=1 -sOutputFile="$out" "$f"

done
