### Query Parser to ETD_DB

### DB.config
This is a configuration file for db connection.

### etd_QUERY.py
This parser will query the pates_etds (i.e., ETD Database -- consits of 500K ETDs).
The parser will connect to the DB and perform a simple query and save the id and title 
field from the database.

Output file: etddb_title.csv

### etd_ID-find.py
This python script takes two input:
* etddb_title.csv (i.e., output file from DB)
* title_metadata.csv (i.e., 500 scanned ETD title metadata (Ground Truth))

Output file: 
* etdmatch.csv
* **ETD_id.csv (i.e., contains final output)**
