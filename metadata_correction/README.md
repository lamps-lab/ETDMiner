This application is to imporve the quality of the metadata fields of Electronic Theses and Dissertations by filling out the missing metadata in the database. We have collected a total of 500K ETDs from different universites and harvested those ETDs in the database. We are using 
[Autometa](https://github.com/lamps-lab/AutoMeta) with visual features to imporve the quality of the metadata.

#### Repository contains:
* evaluation/ -- contains the evaluation code.
* model/ -- contains the model that AutoMeta utilizes.
* src/ -- contains metadata imporvement code using AutoMeta.

#### Steps


##### 1. Clone the following repository:

```
git clone git@github.com:lamps-lab/ETDMiner.git
cd ETDMiner/metadata_correction/src/
```

* As of now, the ETDs are expected to be at ```ETDMiner/metadata_correction/src/etdrepo/``` 

##### 2. Install requirement.txt  and Run the shell script to extract metadata using AutoMeta.
 
```
python -m pip install -r requirements.txt
$./extract_metadata.sh 
``` 

This script takes PDFs ETD as input and output a CSV file containing their Metadata. The intermediate steps are as below.

(a) Obtain the cover page from the PDF and convert it to TIF format.
(Currently, the first page of an ETD is assumed to be the cover page in all cases).

(b) Use Tesseract OCR to extract the text from the TIF image as well as the hOCR output.

(c) To make the extracted text files the same format as the input to the CRF model (XML format), adding dummy tags.

(d) To add the visual features, the script will execute visual_features.py and read all the .html files from hocr/ directory and get the visual information and save the result into visual_features/ directory. However, the
final output (i.e., visual_features_test.csv) will be save into CRF_output/ directory.

(e) Using the CRF-visual model to make predictions 

* The output will be a CSV file containing metadata for each ETD.

File Location: CRF_output/metadata_visual.csv

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
 
##### Future Work:

* Allow a user to provide a list of ETDs (path to ETDs) on which to run the entire process.
* Determine which page of an ETD is the cover page intelligently (on progress).
