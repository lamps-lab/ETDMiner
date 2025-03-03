
import fitz
import glob
from timeit import default_timer as timer
import os.path
from os import path
import pprint
import click


def entrypoint(i,filepath,pageToRun):

    error_out=open("results/Error_List.txt","a")
#     for pageToRun in pagesToRun:
    outfile=open("results/0"+str(i)+"_ocr_page"+str(pageToRun)+".txt", "a")

    try:
        with fitz.open(filepath) as doc:
            totalPages = doc.page_count
            if pageToRun < totalPages:
                ret_string=str(get_scanned_pages_percentage(filepath,i,pageToRun))

                if ret_string=="Scanned not OCR":
                    outfile.write(filepath+ ","+ ret_string+'\n')
                elif ret_string=="0.0":
                    outfile.write(filepath+ ","+ "Born Digital"+'\n')
                else:
                    outfile.write(filepath+ ","+ "OCR"+'\n')

    except Exception as e:
        error_out.write("Error in file "+filepath+" "+str(e)+'\n')
#         print("error in file"+ filepath+" "+str(e))


class NoTextPagesException(RuntimeError):
    pass


def get_scanned_pages_percentage(filepath,foldernum,pageToRun):
    """
    Return the percentage of pages with text which were scanned.
    Note that this could raise a NoTextPagesException.
    """
#     recheckFile=open("recheck_"+str(foldernum)+".txt","a")
    total_pages = 0
    total_scanned_pages = 0

    with fitz.open(filepath) as doc:
#         for page in doc:
        page=doc[pageToRun]
        text = page.getText().strip()
        if len(text) == 0:
            
            total_pages = 0
#             recheckFile.write(str(filepath)+"\n")
        
        else:
            total_pages += 1
        pix1 = page.getPixmap(alpha=False)  # render page to an image
#         pix1.writePNG(f"page-{page.number}.png")  # store image as a PNG
        remove_all_text(doc, page)
        pix2 = page.getPixmap(alpha=False)
#         pix2.writePNG(f"page-{page.number}-no-text.png")
        img1 = pix1.getImageData("png")
        img2 = pix2.getImageData("png")
        if img1 == img2:   
            
            total_scanned_pages += 1
        elif img1!=img2:
#             print("len"+str(len(img1)))
#             print(len(img2))
            if(len(img1)-len(img2)<10000):
#                 recheckFile.write(filepath+"\n")
                total_scanned_pages += 1
            else:
                total_scanned_pages += 0

    
    if total_pages == 0:
        
  
        return "Scanned not OCR"

    else:
        return str(total_scanned_pages / total_pages)


def remove_all_text(doc, page):
    
    page.cleanContents()  # syntax cleaning of page appearance commands

    # xref of the cleaned command source (bytes object)
    xref = page.getContents()[0]

    cont = doc.xrefStream(xref)  # read it
    ba_cont = bytearray(cont)  # a modifyable version
    pos = 0
    changed = False  # switch indicates changes
    while pos < len(cont) - 1:
        pos = ba_cont.find(b"BT\n", pos)  # begin text object
        if pos < 0:
            break  # not (more) found
        pos2 = ba_cont.find(b"ET\n", pos)  # end text object
        if pos2 <= pos:
            break  # major error in PDF page definition!
        ba_cont[pos : pos2 + 2] = b""  # remove text object
        changed = True
    if changed:  # we have indeed removed some text
        doc.updateStream(xref, ba_cont)  # write back command stream w/o text





if __name__ == "__main__":
    for i in range(0,9):
        print("I am working on"+str(i))
        # file="15983.pdf"
        path="/mnt/research-data/etdrepo/00"+str(i)+"/"
        pagesToRun=46
#         print(path)
#     #     print(path+'/*/*.pdf')
        for file in glob.glob(path+"*/"+"*.pdf"):
            #print(file)
            if str(os.path.isfile(file)):
    #             
                entrypoint(i,file,pagesToRun)
# print(path +" is done")

    
    
