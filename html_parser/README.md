# HTML Parser for ProQuest webpages

The following Python program was written to receive dissertation as an html file. 

Parse the HTML dissertations using BeautifulSoup to extract metadata from articles to store as JSON objects and then insert them into SQL database.

# How to run the program
In the command line to specify arguments,
$ python parser.py --help or -h will show all the options
  
The arguments to choose from are the following:  

The path to the directory is required to run the program
--path or -p to input the path for the HTML files ending with /  

OR  

Users can also specify the University they would like to retreive data from with the argument --uni  

# Expected output
parser.py will then store the JSON objects in a file called data.json
  
Then, the next Python file will read the data and insert into SQL database

# Details

Each ProQuest Dissertation holds metadata under the same   
div class = "content display_record_section_indexing"  

They follow the same structure about the data:  
    div class = "display_record_indexing_row"  
		div class = "display_record_indexing_fieldname"  
			div class = "display_record_indexing_data"  


Certain universities do not have the same number of dataFields.  
As an example, University of Arkansas at Pine Bluff does not have Advisor and Committee member field
Norfolk State University does not have Department attribute

However, they all have the same name for each dataField if they exist within the details.

The Abstract is stored in class="abstract truncatedAbstract"  
