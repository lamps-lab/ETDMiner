# HTML Parser

The following Python program was written to receive dissertation as an html file. 

Parse the html dissertations using BeautifulSoup to extract metadata from articles to store as JSON objects and then insert them into SQL database.

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
