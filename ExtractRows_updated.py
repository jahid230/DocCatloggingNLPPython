# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 09:35:29 2020

@author: jahid
"""
import json
import numpy
import array
import re


with open("output-1-to-2.json", "r",encoding="utf8") as read_file:
    
  
    data = json.load(read_file)
    
    inputConfigobject=data.get('responses')
    #print(inputConfigobject[0].items())
    page_array=dict()
    block_page=dict()
    lineBreakLocation=dict()
    wordList=dict()
    wordswithSpace=dict()
    rowsData=dict()
    rows=[]
    rowsw=dict()
    linebreak=dict()
    t2=dict()
    columnData=dict()
    spaceThreshold=.01
    i=0
    y_diff=[]
    y_list=[]
    x_diff=[]
    x_list=[]
    x_list_sorted=[]
    #x_diff.append(0)
    #y_diff.append(0)
    y_list.append(0)
    x_list.append(0)
    line_spacing_arr=[]
    index=0
    rowsIndex=1
    tt=1
    lineSpacedict=dict()
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
                     t=0
                     for singleBlock in page_obj[0]['blocks']:
                         blockId=str(page_obj[0]['blocks'].index(singleBlock))
                         for k2,v2 in  singleBlock.items():
                             
                             if(k2=='paragraphs'):
                                 for k3,v3 in v2[0].items():
                                     
                                     if(k3=='words'):
                                         singleRow = []
                                         rowInnerIndex=0
                                         for singleWord in v3:
                                             wordIndex=str(v3.index(singleWord))
                                             wordId="P"+str(i)+"B"+blockId+"W"+wordIndex
                                             lastWordofLine=""
                                             locationoflineEnding=singleWord['boundingBox']['normalizedVertices'][2]
                                             locationofStart=singleWord['boundingBox']['normalizedVertices'][3]
                                             xVal=locationofStart.get('x')
                                             yVal=locationoflineEnding.get('y')
                                             y_list.append(yVal)
                                             x_list.append(xVal)
                                           
                                             current_y_diff=abs(y_list[index+1]-y_list[index])
                                             current_x_diff=abs(x_list[index+1]-x_list[index])
                                             index +=1
                                             # numpy.sort(y_list)
                                             # val100=numpy.argsort(x_list)
                                             # x_list_sorted.append(val100[-1])
                                             
                                             for singleSymbol in singleWord['symbols']:
                                                  symbolText=singleSymbol.get('text')
                                                  lastWordofLine=lastWordofLine+symbolText
                                                  wordVal={wordId:[lastWordofLine,xVal,yVal]} 
                                             wordList.update(wordVal) 
    
    
    
    
    
    headerInfo=dict()
    bodyBlocks=dict()
    rowFirstitem=dict()
    ci=[]
    nn=[]
    pt=[]
    diff=0
    start=True
    headerString=""  
    currentString=""
    currentBlock=0
    i=0
    rowI=0
    a=0
    b=0
       
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
           
    
                             
    po=0 
    lm=[]
    colInfo=dict()
    startPos=True
    index=0
   
    po=0
    sd=[]        
    startCount=True
    startCol=True
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
            print(po,key2,Val2[0], bodyBlocks.get(nextWord))
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
  
     
print("end")  