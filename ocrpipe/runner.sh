#!/usr/bin/env bash

PDFDIR=/tmp/pdfs
TIFDIR=/tmp/tifs
mkdir -p $TIFDIR

for p in "$@"
do
    pdf=$PDFDIR/$p

    echo "Processing $pdf"

    gs -o $TIFDIR/page-%d.tif -sDEVICE=tiff24nc -r300x300 $pdf
done

rm -rf $TIFDIR
