import urllib.request
import urllib.response
import urllib.parse
import bs4
import re
import time
from collections import defaultdict
import json
import os


def createProjectFolder():
    folder_location = r'E:\psu_files'
    if not os.path.exists(folder_location):
        os.mkdir(folder_location)


def createUrlList(url, page_num):  # creates a url link for every page of the psu website
    url_index = []  # container for the url's
    for i in range(1, page_num):
        url_index.append(url + str(i))  # creates a link for every page and stores it into a list

    return url_index


def getReponse(url):  # gets a response for each url
    header= {}
    header['user_agent'] = "Mozilla/5.0 (X11; Linux x86_64)"
    header["From"] = "tdenn007@odu.edu"

    req = urllib.request.Request(url,headers=header)
    response = urllib.request.urlopen(req)
    time.sleep(10)  # delays the program 10 secs so it doesn't get blocked
    response = response.read()
    return response


def getLink(response, domain):  # extracts the catalog links from each page
    links = []
    soup = bs4.BeautifulSoup(response, "html.parser")
    for link in soup.find_all("a", attrs={'href': re.compile("^/catalog/")}):  # grabs the link using regular expression
        catalog = link.get('href')
        links.append(domain + str(catalog))  # creates a full url for the program to follow
    return links


def parseMetadata(link, id):  # grabs all the metadata for each paper
    psu_papers = defaultdict(dict)  # a nested dict for all the information to be stored

    response = urllib.request.urlopen(link)  # opens each link to be parsed
    response = response.read()
    time.sleep(5)  # delays the program
    link_soup = bs4.BeautifulSoup(response, "html.parser" )

    title = link_soup.find('h1', attrs={"itemprop": "name"})  # parsing the metadata
    author = link_soup.find('dd', class_="blacklight-author_name_tesi")
    program = link_soup.find('dd', class_="blacklight-program_name_ssi")
    degree = link_soup.find('dd', class_="blacklight-degree_description_ssi")
    doc_type = link_soup.find('dd', class_="blacklight-degree_type_ssi")
    date = link_soup.find('dd', class_="blacklight-defended_at_dtsi")
    members = link_soup.find('dd', class_="blacklight-committee_member_and_role_tesim")
    keywords = link_soup.find('dd', class_="blacklight-keyword_ssim")
    abstract = link_soup.find('dd', class_="blacklight-abstract_tesi")

    psu_papers[id]['id'] = str(id)  # storing the metadata
    if title is not None:

        psu_papers[id]['title'] = title.getText().strip('\n')
    else:
        psu_papers[id]['title'] = "NaN"

    if author is not None:

        psu_papers[id]['author'] = author.getText().strip('\n')
    else:
        psu_papers[id]['author'] = "NaN"

    if program is not None:

        psu_papers[id]['program'] = program.getText().strip('\n')
    else:
        psu_papers[id]['program'] = "NaN"

    if degree is not None:

        psu_papers[id]['degree'] = degree.getText().strip('\n')
    else:
        psu_papers[id]['degree'] = "NaN"

    if doc_type is not None:

        psu_papers[id]['doc_type'] = doc_type.getText().strip('\n')
    else:
        psu_papers[id]['doc_type'] = "NaN"

    if date is not None:

        psu_papers[id]['date'] = date.getText().strip('\n')
    else:
        psu_papers[id]['date'] = "NaN"

    if members is not None:

        psu_papers[id]['members'] = members.getText().strip('\n')
    else:
        psu_papers[id]['members'] = "NaN"

    if keywords is not None:

        psu_papers[id]['keywords'] = keywords.getText().strip('\n')
    else:
        psu_papers[id]['keywords'] = "NaN"

    if abstract is not None:

        psu_papers[id]['abstract'] = abstract.getText().strip('\n')
    else:
        psu_papers[id]['abstract'] = "NaN"

    if link is not None:

        psu_papers[id]['link'] = link
    else:

        psu_papers[id]['link'] = "NaN"

    return psu_papers


def writePDF(pdf_file_name, pdf_link):
    f = open(pdf_file_name, 'wb')
    f.write(requests.get(pdf_link, allow_redirects=True).content)
    f.close()


def extractPDF(link, domain, id):  # extracting the pdf from website this function is giving me trouble
    psu_pdf = defaultdict(dict)  # nested dict for the pdf info

    response = urllib.request.urlopen(link)
    response = response.read()
    time.sleep(5)
    link_soup = bs4.BeautifulSoup(response, "html.parser")
    pdf_link = link_soup.find("a", attrs={'href': re.compile("^/files/")})  # grabs the link for the pdf

    pdf_name = "psu_pdf_" + str(id) + ".pdf"  # creates the pdf with unique ID

    if pdf_link != None:  # check if beautifulsoup grabbed nothing
        pdf = domain + pdf_link['href']  # creates url
        print("exporting...."+ pdf_name)
        urllib.request.urlretrieve(pdf,
                                   pdf_name)  # this is where the problem is. It should download the pdf to the file name created
        psu_pdf[id]["id"] = str(id)  # stores info on pdf
        psu_pdf[id]["PDF_filename"] = pdf_name
        psu_pdf[id]["PDF_link"] = pdf

    else:
        psu_pdf[id]["id"] = str(id)
        psu_pdf[id]["PDF_filename"] = pdf_name
        psu_pdf[id]["PDF_link"] = "NaN"  # if bs4 grabbed nothing it gives this answer to know data is missing

    return psu_pdf


def writeFile(metadata, id):  # writes to json file
    metadata_filename = "psu_metadata_" + str(id) + ".txt"
    with open(metadata_filename, 'w') as output_file:
        json.dump(metadata, output_file)
    print("exporting ... " + metadata_filename)


def getWebsite(url, page_num, domain):  # all the functions under the same roof
    url_list = []
    links_list = []

    id = 1

    url_list = createUrlList(url, page_num)
    for item in url_list:
        response = getReponse(item)
        links_list = getLink(response, domain)
        for link in links_list:
                metadata = parseMetadata(link, id)
                extractPDF(link, domain, id)
                writeFile(metadata, id)
                id = id + 1


if __name__ == '__main__':  # execution of program
    domain = "https://etda.libraries.psu.edu"  # the base domain
    url = "https://etda.libraries.psu.edu/catalog?page="  # the url without the page number
    page_num = 1567 # number of pages you want to scrape
    getWebsite(url, page_num, domain)  # program
