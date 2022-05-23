#### File Structure

AutoMeta
```
 — CRF_output
 — etdrepo
 — hocr
 — tif
 — txt
 — xml	
 — code
  — extract_metadata.sh
  — anomaly_detect.py
  — updateDB.py
  — updateDB.config
  — crf-test.py
  — dummy_tags.py
  — process_crf_result.py
  — tesseract_ocr_hocr.py
```

#### Steps


##### 1. Clone this repository and run file_structure.sh

```
git clone git@github.com:lamps-lab/ETDMiner.git
cd ETDMiner/metadata_correction/src/ 
./file_structure.sh
```

* As of now, the ETDs are expected to be at ```ETDMiner/metadata_correction/src/etdrepo/``` 

##### 2. Run this script to extract metadata using AutoMeta.
 
```
$./extract_metadata.sh 
``` 

This script takes PDFs ETD as input and output a CSV file containing their Metadata. The intermediate steps are as below.

(a) Obtain the cover page from the PDF and convert it to TIF format.
(Currently, the first page of an ETD is assumed to be the cover page in all cases)

(b) Use Tesseract OCR to extract the text from the TIF image as well as the hOCR output.

(c) To make the extracted text files the same format as the input to the CRF model (XML format), adding dummy tags.

(d) Using the CRF model to make predictions 

* The output will be a CSV file containing metadata for each ETD.

File Location: CRF_output/metadata.csv

##### 3. Use the extracted metadata to update the missing values in the original ETD database.

* ```updateDB.config``` is the configutation file. This is where you enter your database login information and set database settings.

```
[SERVER_CONFIG]

HOST = hawking.cs.odu.edu
USER = username_for_hawking
PASSWORD = password_for_hawking

[DATABASE_CONFIG]
DATABASE = pates_etds (Database name)
ETD_TABLE = orig_etd_tablename
ETD_TABLE_LIMIT = all (OR set this to any numerical value (< total no. of rows in orig etd table) which will decide how many rows in the database to be considered as input)
SHADOW_TABLE = shadow_tablename

[METADATA_UPDATE_CONFIG]
	
ORIG_METHOD = library
UPDATE_METHOD = autometa
```

* The ```updateDB.py``` code will conduct the following operations.

1. This code iterates through each row in the original ETD table to look for missing values.
2. If a missing value(s) is found, it would check the metadata miner autoMeta to obtain the missing values. 
3. If missing values are available in the CSV file obtained as output from autoMeta, the original ETD table will be updated with these data while the original row is backed up in the new shadow table. 
4. The orig ETD table will have a new version number incremented by 1.

 ```$ python3 updateDB.py ``` 
 
##### Future:

* Incorporate visual features for predictions using CRF model.
* Allow a user to provide a list of ETDs (path to ETDs) on which to run the entire process.
* Determine which page of an ETD is the cover page intelligently.
