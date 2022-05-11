
#### File Structure

AutoMeta
```
 — etdrepo
 — hocr
 — tif
 — txt
 — xml	
 — code
  — anomaly_detect.py
  — autometa.py
  — conversion.sh
  — crf-test.py
  — dummy_tags.py
  — extract.sh
  — process_crf_result.py
  — tesseract_ocr_hocr.py
```

#### Steps

##### 1. Get metadata extracted using AutoMeta
 
(a) Obtain the cover page from the PDF and convert it to TIF format.
(Currently, the first page of an ETD is assumed to be the cover page in all cases)

```
For step (a),
$./conversion.sh 
```
(b) Use Tesseract OCR to extract the text from the TIF image as well as the hOCR output.

(c) To make the extracted text files the same format as the input to the CRF model (XML format), adding dummy tags.

```
For both steps (b) and (c),

$./extract.sh 
``` 
(d) Using the CRF model to make predictions 

``` 
$python3 crf-test.py /home/marsh/Documents/Research/ETD/ETDMinerStuff/testETDs/xml crf_model.sav CRF_output/intermediate.csv
```
