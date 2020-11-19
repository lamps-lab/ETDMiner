#!/usr/bin/env bash

# Change into the "pdf" directory to find the input files
cd pdf || { echo ERROR: Subdirectory tif not found; exit 1; }

# Loop through all files ending in ".pdf"
for f in *.pdf;

do

# Determine output filename
out=${f%%pdf}
#out="../tif/${out}tif"
out="../png/${out}png"

# Show the command we would run - TIFF
#gs -q -sDEVICE=tiffg4 -r300 -dBATCH -dPDFFitPage -dNOPAUSE -dFirstPage=1 -dLast#Page=1 -sOutputFile="$out" "$f"

# Show the command we would run - PNG
gs -q -sDEVICE=png16m -r300 -dBATCH -dPDFFitPage -dNOPAUSE -dFirstPage=3 -dLastPage=3 -sOutputFile="$out" "$f"
done
