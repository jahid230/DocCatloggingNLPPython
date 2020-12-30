# -*- coding: utf-8 -*-
"""
Created on Tue Nov 18 10:07:19 2020

@author: Jahid230
"""



"""Implenting Google cloud Vision API :: Default Pages to be  extacted is sat as 2 """

def async_detect_document(gcs_source_uri, gcs_destination_uri,number_of_pages):
    """OCR with PDF/TIFF as source files on GCS"""
    import json
    import re
    import os
    from google.cloud import vision
    from google.cloud import storage
    from google.protobuf.json_format import MessageToJson

    # Supported mime_types are: 'application/pdf' and 'image/tiff'
    mime_type = 'application/pdf'

    # How many pages should be grouped into each json output file.
    batch_size = number_of_pages

    client = vision.ImageAnnotatorClient()

    feature = vision.Feature(
        type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)

    gcs_source = vision.GcsSource(uri=gcs_source_uri)
    input_config = vision.InputConfig(
        gcs_source=gcs_source, mime_type=mime_type)

    gcs_destination = vision.GcsDestination(uri=gcs_destination_uri)
    output_config = vision.OutputConfig(
        gcs_destination=gcs_destination, batch_size=batch_size)

    async_request = vision.AsyncAnnotateFileRequest(
        features=[feature], input_config=input_config,
        output_config=output_config)

    operation = client.async_batch_annotate_files(
        requests=[async_request])

    print('Waiting for the operation to finish.')
    operation.result(timeout=420)
    
    
    outputFileName='Json'+os.path.basename(gcs_source_uri)+'.json'
    #DOWNLOADING THE THE OBJECT THAT IS CONVERTED
    storage_client = storage.Client()
    
    #LOCATION IN THE CLOUD BUCKET
    bucket_name="mypdf_1"
    bucket = storage_client.bucket(bucket_name)    
    
    blobs = [(blob, blob.updated) for blob in storage_client.list_blobs(
    bucket_name,
    )]
    # sort and grab the latest value, based on the updated key
    latest = sorted(blobs, key=lambda tup: tup[1])[-1][0]
    string_data = latest.download_as_string()
    json_data=json.loads(string_data)
    # print(string_data)
    with open(outputFileName, 'w') as outfile:
     json.dump(json_data, outfile)
    
    print("Sucessfully Created the json file")
    return json_data


"""Function for Uploading a pdf file into google cloud Bucket"""

from google.cloud import storage
def upload_blob(bucket_name, source_file_name, destination_blob_name):
    
    """Uploads a file to the bucket."""
   

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )



"""Base Filtering Method for the tool"""

def extrat_rows_columns(JsonFileObject):
    inputConfigobject=JsonFileObject.get('responses')
    #print(inputConfigobject[0].items())
    page_array=dict()
    block_page=dict()
    wordList=dict()
    totalextraction=dict()
    
    i=0
    y_list=[]
    x_list=[]
    y_list.append(0)
    x_list.append(0)
    index=0
    for each_page_data in inputConfigobject:
     i=i+1
     wordId=""
     for k,v in each_page_data.items():
         if(k=='fullTextAnnotation'):
             #print((type(v)))
             for k1,v1 in v.items():
                 if(k1=='text'):
                   var=1
                   # print('\n',(v1))
                 elif(k1=='pages'):
                     page_obj=v1
                     block_cont=page_obj[0]['blocks']
                     block_cont={i:block_cont}
                     block_page.update(block_cont)
                     page_cont={i:v1}
                     page_array.update(page_cont)
                    
                     for singleBlock in page_obj[0]['blocks']:
                         blockId=str(page_obj[0]['blocks'].index(singleBlock))
                         for k2,v2 in  singleBlock.items():
                             
                             if(k2=='paragraphs'):
                                 for k3,v3 in v2[0].items():
                                     
                                     if(k3=='words'):
                                        
                                         for singleWord in v3:
                                             wordIndex=str(v3.index(singleWord))
                                             wordId="P"+str(i)+"B"+blockId+"W"+wordIndex
                                             lastWordofLine=""
                                             #geting the location of the word
                                             locationoflineEnding=singleWord['boundingBox']['normalizedVertices'][2]
                                             locationofStart=singleWord['boundingBox']['normalizedVertices'][3]
                                             xVal=locationofStart.get('x')
                                             yVal=locationoflineEnding.get('y')
                                             y_list.append(yVal)
                                             x_list.append(xVal)  
                                             index +=1
                                             
                                             for singleSymbol in singleWord['symbols']:
                                                  symbolText=singleSymbol.get('text')
                                                  lastWordofLine=lastWordofLine+symbolText
                                                  wordVal={wordId:[lastWordofLine,xVal,yVal]} 
                                             #Inset a word into the dictionary
                                             wordList.update(wordVal) 
                                             
                                             
                                             
    headerInfo=dict()
    bodyBlocks=dict()
    rowFirstitem=dict()
    ci=[]
    nn=[]
 
    start=True
    headerString=""  
    currentString=""
    currentBlock=0
    i=0
    rowI=0
    a=0
    b=0
    
    ## The following block extracts the header and rows from the word list
    for keyD,keyV in wordList.items():
        pagePivot=keyD.find("P")
        blockPivot=keyD.find("B")
        wordPivot=keyD.find("W")
        pageNum=keyD[pagePivot+1:blockPivot]
        blockNum=keyD[blockPivot+1:wordPivot]
        wordNum=keyD[wordPivot+1:]
        
        # print(keyV[2])
        if(start):
            temp=keyV[2]
            start=False
        if(keyV[2]==temp):
            if(keyD=='P1B0W0'):
                rowFirstitem.update({rowI:keyV})
            bodyBlocks.update({keyD:[rowI,keyV]})
            # print(keyV)
            i+=1
        else:
            i=0
            temp=keyV[2]
            rowI+=1
            rowFirstitem.update({rowI:keyV})
            bodyBlocks.update({keyD:[rowI,keyV]})
        
        if(int(pageNum)==1):
            if(int(blockNum)==0):
                headerString=headerString+keyV[0]
                ci.append(keyV[0])
                headerInfo.update({pageNum+"B"+blockNum:headerString}) 
            elif(int(blockNum)==currentBlock):
                a=b
               
            else:
                currentBlock=int(blockNum)
                if(start):
                 start=False
        else:
          if(int(blockNum)==0):
              # print(currentString)
              if(currentString in headerString) and (len(currentString)>int(0.65*len(headerString))):
                  # print("headerMatches")
                  nn.append(currentString)
                  headerInfo.update({pageNum+"B"+blockNum:nn}) 
              else:
                  # print(len(currentString),len(headerString))
                  currentString=currentString+keyV[0]
          else:
              currentString=""
           
    
    totalextraction.update({"header":headerInfo})
    totalextraction.update({"rows":bodyBlocks})                             
    po=0 

    colInfo=dict()
  
    index=0
   
    po=0
    sd=[]        
    
    h=0
    inp=0
    nt=[]
    ind=1
    nt.append(0)
    for key2,Val2 in bodyBlocks.items():
        pagePivot=key2.find("P")
        blockPivot=key2.find("B")
        wordPivot=key2.find("W")
        pageNum=key2[pagePivot+1:blockPivot]
        blockNum=key2[blockPivot+1:wordPivot]
        wordNum=key2[wordPivot+1:]
        
        ind+=1
        if(po==Val2[0]):
            nextWord="P"+pageNum+"B"+blockNum+"W"+str(int(wordNum)+1)
            sd.append(Val2)
            po=Val2[0]+1
            
            if(len(sd)==1):
                continue
            else:
                if(sd[h][1][1]==sd[h+1][1][1]):
                    # print(sd[h][1],sd[h+1][1])
                    if(inp==0):
                        colInfo.update({inp:[po-2,sd[h][1]]})
                        inp+=1
                        colInfo.update({inp:[po-1,sd[h+1][1]]})
                        inp+=1
                    else:
                        if(colInfo.get(inp-1)[1][2]==sd[h][1][2]):
                            colInfo.update({inp:[po-1,sd[h+1][1]]})
                            inp+=1
                        else:
                            colInfo.update({inp:[po-2,sd[h][1]]})
                            inp+=1
                            colInfo.update({inp:[po-1,sd[h+1][1]]})
                            inp+=1
                
                h+=1
    print("End")
    totalextraction.update({"columns":colInfo})
    
    ##returning the dictonary object
    return totalextraction   



"""Base Function for the Filtering"""


def pdf_extraction(filePath):
    import json
    import os
    from PyPDF2 import PdfFileReader
    
    
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = ''
  
    fileName=os.path.basename(filePath)
    
    ##Upload the file into googel cloud storage bucket
    ##Param 1: the cloud Storage Bucket Name
    # Pram 2: file path of the pdf
    ## Param 3: file name of the file 
    
    upload_blob("mypdf_1",filePath,fileName)
    
    
    ## google cloud Vision Api Call for getting the json output 
    
    #source file for extraction
    gcs_source_uri="gs://mypdf_1/"+fileName+""
   
    #download destination for the cloud bucket
    gcs_destination_uri="gs://mypdf_1/"
    
    ## Get the batch size of the PDF
    
    pdf=PdfFileReader(open(filePath,'rb'))
    number_of_pages=pdf.getNumPages()
    #api call for the pdf to json extraction    
    JsonFileObject=async_detect_document(gcs_source_uri, gcs_destination_uri,number_of_pages)
    
    ##PDF extraxtion and filtering the data with row and column Extraction
    
    finalOutputDict=extrat_rows_columns(JsonFileObject)
    
    
    print(finalOutputDict)
   ##Saving the file as json file
   
   ##The folowing code depends on the environment
    # outputFileNameNew='/dataSource/filtered-Output/'+'FilteredJSON.json'
    # print(outputFileNameNew)
   
    # with open(outputFileNameNew, 'w') as outfile:
    #  json.dump(finalOutputDict, outfile)    
                  




"""Base Function for the tool"""

import sys

sys.stdout.write("hello from Python %s\n" % (sys.version,))

path = '/dataSource/fileName.pdf'

pdf_extraction(path)


    
