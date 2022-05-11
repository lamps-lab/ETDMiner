
#### File Structure

AutoMeta
```
 — etdrepo
 — hocr
 — tif
 — txt
 — xml	
 code
```

#### Steps

1. Get metadata extracted using AutoMeta

For step (a),

``` $./conversion.sh ```

(a) Obtain the cover page from the PDF and convert it to TIF format.
(Currently, the first page of an ETD is assumed to be the cover page in all cases)

For both steps (b) and (c),

``` $./extract.sh ``` 

(b) Use Tesseract OCR to extract the text from the TIF image as well as the hOCR output.

(c) To make the extracted text files the same format as the input to the CRF model (XML format), adding dummy tags.

For
``` $ ```

Using the CRF model to make predictions 
 ``` $python3 crf-test.py /home/marsh/Documents/Research/ETD/ETDMinerStuff/testETDs/xml crf_model.sav CRF_output/intermediate.csv  ```
