#!/usr/bin/env bash

# Change into the "tif" directory to find the input files
cd pdf || { echo ERROR: Subdirectory tif not found; exit 1; }

# Loop through all files ending in ".tif"
for f in *.pdf;

do

# Determine output filename
out=${f%%pdf}
out="../tif/${out}tif"

# Show the command we would run
gs -q -sDEVICE=tiffg4 -r300 -dBATCH -dPDFFitPage -dNOPAUSE -dFirstPage=1 -dLastPage=1 -sOutputFile="$out" "$f"

done
