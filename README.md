# ETDMiner
Programs and tools collected and developed to mine electronic theses and dissetations.

# Description:

# ocrpipe:
It contains two files - a.) Dockerfile b.)runner.sh
# Dockerfile:
 
	- The Dockerfile is automating the process of converting the ETD samples/datasets (pdf format) to .tif format.
	
	- Also, it has all the necessary pipelines to download the packages such as Tesseract-OCR and Ghostscript
	
	- To build the image, the following command can be executed: 
		
		docker image build -t ocrpipe .
	
	- For running the docker container, the follwoing command can be executed after building the image:
		
		docker container run --rm -it -v /tmp/tifytest:/tmp/pdfs -v /tmp/tifout:/tmp/tifs ocrpipe sample1965.pdf
	
	- Note, for testing purpose /tmp/tifytest has been created and this directory has been mounted with /tmp/pdfs (it contains the sample dataset in pdf)
	  and the directory /tmp/tifout has been mounted with /tmp/tifs (it contains the output in .tif format)
# runner.sh:
	
	- It is a simple bashscript in order to iterate through pages from a pdf and convert it into .tif format.
	
	- Basically, it contains Ghostscript command in the loop to get this job done
	
	- In the beginning of the script, PDFDIR is the directory where the pdf sample will be existed and TIFDIR is the directory
	  where it be containing all the output files (.tif formats of the pdf)
	
	- Note, everytime this runner.sh will be executed during the process of rebuilding the image and run the docker container on new pdf,
	  the /tmp/tifout directory will be removing the previous .tif images and will have the new images for new sample.

samples:
It contains the sample dataset which has been tested out in the above process

src:
It contains the "tesseract.py" script. After executing the Dockerfile, run this script on the sample output (.tif format)

images:
It contains the sample output images in .tif format (paper-1 to paper-7) along with the output of the tesseract result (HOCR_result and paper-1_result)   
	
	
		