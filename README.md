#### Table of Contents

- [ETDMiner](#etdminer)
- [Description:](#description)
- [ocrpipe:](#ocrpipe)
- [Dockerfile:](#dockerfile)
- [runner.sh:](#runnersh)
- [samples:](#samples)
- [src:](#src)
- [ocr_experimented_images:](#ocr-experimented-images)
- [webcrawler](#webcrawler)
- [Metadata Correction](#metadata-correction)  

<small><i><a href='http://ecotrust-canada.github.io/markdown-toc/'>Table of contents generated with markdown-toc</a></i></small>


# ETDMiner
Programs and tools collected and developed to mine electronic theses and dissetations.

# Description

# ocrpipe
It contains two files - a.) Dockerfile b.)runner.sh

# Dockerfile
 
- The Dockerfile is automating the process of converting the ETD samples/datasets (pdf format) to .tif format.
	
- Also, it has all the necessary pipelines to download the packages such as Tesseract-OCR and Ghostscript
	
- To build the image, the following command can be executed: 
		
		docker image build -t ocrpipe .
	
- For running the docker container, the follwoing command can be executed after building the image:
		
		docker container run --rm -it -v /tmp/tifytest:/tmp/pdfs -v /tmp/tifout:/tmp/tifs ocrpipe sample1965.pdf
	
- Note, for testing purpose /tmp/tifytest has been created and this directory has been mounted with /tmp/pdfs (it contains the sample dataset in pdf) and the directory /tmp/tifout has been mounted with /tmp/tifs (it contains the output in .tif format)

# runner.sh
	
- It is a simple bashscript in order to iterate through pages from a pdf and convert it into .tif format.
	
- Basically, it contains Ghostscript command in the loop to get this job done
	
- In the beginning of the script, PDFDIR is the directory where the pdf sample will be existed and TIFDIR is the directory where it will be containing all the output files (.tif formats of the pdf)
	
- Note, everytime this runner.sh will be executed during the process of rebuilding the image and run the docker container on new pdf,
the /tmp/tifout directory will be removing the previous .tif images and will have the new images for new sample.

# samples
It contains the sample dataset which has been tested out in the above process

# src
It contains the "tesseract.py" script. After executing the Dockerfile, run this script on the sample output (.tif format)

# ocr_experimented_images
It contains the sample output images in .tif format (paper-1 to paper-7) along with the output of the tesseract result (HOCR_result and paper-1_result)   

# webcrawler
Contains the crawlers & parsers for different universities developed to collect ETDs and extract metadata from the webpages.
	
# Metadata Correction

[Go to the sub-folder](metadata_correction/src/)

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
