#!/usr/bin/env python3
# -*- coding: utf-8 -*-



#Detects text in a document stored in an S3 bucket. Display polygon box around text and angled text 
import boto3
import io
from io import BytesIO
import sys
import json
import os

import psutil
import time

import math
from PIL import Image, ImageDraw, ImageFont


# Displays information about a block returned by text detection and text analysis
def DisplayBlockInformation(block):
    print('Id: {}'.format(block['Id']))
    if 'Text' in block:
        print('    Detected: ' + block['Text'])
    print('    Type: ' + block['BlockType'])
   
    if 'Confidence' in block:
        print('    Confidence: ' + "{:.2f}".format(block['Confidence']) + "%")

    if block['BlockType'] == 'CELL':
        print("    Cell information")
        print("        Column:" + str(block['ColumnIndex']))
        print("        Row:" + str(block['RowIndex']))
        print("        Column Span:" + str(block['ColumnSpan']))
        print("        RowSpan:" + str(block['ColumnSpan']))    
    
    if 'Relationships' in block:
        print('    Relationships: {}'.format(block['Relationships']))
    print('    Geometry: ')
    print('        Bounding Box: {}'.format(block['Geometry']['BoundingBox']))
    print('        Polygon: {}'.format(block['Geometry']['Polygon']))
    
    if block['BlockType'] == "KEY_VALUE_SET":
        print ('    Entity Type: ' + block['EntityTypes'][0])
    if 'Page' in block:
        print('Page: ' + block['Page'])
    print()

def process_text_detection(bucket, document, i, j):

    
    #Get the document from S3
    s3_connection = boto3.resource('s3')
                          
    s3_object = s3_connection.Object(bucket,document)
    s3_response = s3_object.get()

    stream = io.BytesIO(s3_response['Body'].read())
    image=Image.open(stream)

   
    # Detect text in the document
    
    client = boto3.client('textract')
    #process using image bytes                      
    #image_binary = stream.getvalue()
    #response = client.detect_document_text(Document={'Bytes': image_binary})

    #process using S3 object
    response = client.detect_document_text(
        Document={'S3Object': {'Bucket': bucket, 'Name': document}})

    #Get the text blocks
    blocks=response['Blocks']
    width, height =image.size  
    draw = ImageDraw.Draw(image)  
    file_name = 'Folder_'+str(j)+'/'+ str(i) + '.json'
    file1 = open(file_name,"w")
    print ('Detected Document Text')
    json_list=[]
     
    # Create image showing bounding box/polygon the detected lines/text
    for block in blocks:
            counter1=0
            counter2=0
            if block['BlockType'] != 'PAGE':
                counter1=1
            if 'Relationships' in block:
                counter2=1
            if counter1 ==1 and counter2==1:
                data = {'Type': block['BlockType'],'Id': block['Id'],'Confidence': block['Confidence'], 'Detected': block['Text'],'Geometry':{'Bounding Box': block['Geometry']['BoundingBox']}, 'Polygon': block['Geometry']['Polygon'], 'Relationships': block['Relationships']}
            elif counter1==1 and counter2==0:
                data = {'Type': block['BlockType'],'Id': block['Id'],'Confidence': block['Confidence'], 'Detected': block['Text'],'Geometry':{'Bounding Box': block['Geometry']['BoundingBox']}, 'Polygon': block['Geometry']['Polygon']}
            elif counter1==0 and counter2==1:
                data = {'Type': block['BlockType'],'Id': block['Id'],'Geometry':{'Bounding Box': block['Geometry']['BoundingBox']}, 'Polygon': block['Geometry']['Polygon'], 'Relationships': block['Relationships']}
            else:
                data = {'Type': block['BlockType'],'Id': block['Id'],'Geometry':{'Bounding Box': block['Geometry']['BoundingBox']}, 'Polygon': block['Geometry']['Polygon']}
            json_list.append(data)
       
    file1.writelines(json.dumps(json_list))
         

    
    return len(blocks)

def main():
    bucket = 'scannedetd'
    #change the value of number_of_document with the value of the number of png files to be processed
    number_of_document = 26
    for j in range(1,number_of_document):
        size = 0
        print("Document No: " + str(j))
        for base, dirs, files in os.walk('pngs_1/'+str(j)):
            for Files in files:
                size+=1
        for i in range(1,size+1):
            document = 'pngs_1/'+ str(j)+'/'+str(i)+'.png'
            block_count=process_text_detection(bucket,document,i,j)
            
            print("Blocks detected: " + str(block_count))
    
if __name__ == "__main__":
    main()
