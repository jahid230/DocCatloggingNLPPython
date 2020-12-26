# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 10:07:19 2020

@author: Jahid230
"""



import sys
sys.stdout.write("hello from Python %s\n" % (sys.version,))

import json
import numpy

#from json2table import convert

with open("dataJson.json", "r",encoding="utf8") as read_file:
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
                   #print('\n',(v1))
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
                                             wordId=str(i)+blockId+wordIndex
                                             lastWordofLine=""
                                             locationoflineEnding=singleWord['boundingBox']['normalizedVertices'][2]
                                             locationofStart=singleWord['boundingBox']['normalizedVertices'][3]
                                             xVal=locationofStart.get('x')
                                             yVal=locationoflineEnding.get('y')
                                             y_list.append(yVal)
                                             x_list.append(xVal)
                                           
                                             current_y_diff=abs(y_list[index+1]-y_list[index])
                                             current_x_diff=abs(x_list[index+1]-x_list[index])
                                             y_diff.append(current_y_diff)
                                             x_diff.append(current_x_diff)
                                             index +=1
                                             numpy.sort(x_list)
                                             val100=numpy.argsort(x_list)
                                             x_list_sorted.append(val100[-1])
                                             # x_list_sorted.append(val100)
                                             for items123 in val100:
                                                   t2.update({wordId:[wordId,items123,x_list[items123]]})
                                             
                                         
                                             for singleSymbol in singleWord['symbols']:
                                                  symbolText=singleSymbol.get('text')
                                                  lastWordofLine=lastWordofLine+symbolText
                                                  wordVal={wordId:[lastWordofLine,xVal,yVal,x_list[-1]]}
                                                  
                                                  
                                                  # rowsData.update(wordVal)
                                                  
                                                  columnVal=wordList.get(wordId)
                                                  columnData.update({wordId:[xVal,columnVal]})
                                                  for k4,v4 in singleSymbol.items() :
                                                      if(k4=='property'):
                                                         for k5,v5 in v4.items():
                                                             if(k5=='detectedBreak'):
                                                                 
                                                                 if(v5['type']=='LINE_BREAK'):
                                                                      LineBreakInfo={wordId:[lastWordofLine,xVal,yVal,x_list[-1]]} 
                                                                      lineBreakLocation.update(LineBreakInfo)
                                                                      tlist=list(lineBreakLocation.items())
                                                                      spacebetweenLines=tlist[rowsIndex-1][1][1]
                                                                      diff=spacebetweenLines-tlist[rowsIndex-2][1][1]
                                                                      cont_linespace={rowsIndex-1:spacebetweenLines}
                                                                      cont_diffrential={rowsIndex-1:diff}
                                                                      lineSpacedict.update(cont_linespace)
                                                                      linebreak.update(cont_diffrential)
                                                                      rowsData.update({rowsIndex:LineBreakInfo})
                                                                      # print(rows)
                                                                      
                                                                      
                                                                      lineBreakFlag=1
                                                                      rowsIndex+=1
                                                                      
                                                                      print('\n')
                                                                 elif(v5['type']=='SPACE'):
                                                                      SPCEInfo={wordId:[lastWordofLine,xVal,yVal,x_list[-1]]} 
                                                                      wordswithSpace.update(SPCEInfo)
                                                                      # print(rowInnerIndex)
                                                                      
                                                                      #rowsData.update(SPCEInfo)
                                                                      rowInnerIndex+=1
                                                                      lineBreakFlag=0
                                                                      # print(SPCEInfo)
                                                                      print('\n')
                                                                 else:
                                                                    restOfWord={wordId:[lastWordofLine,xVal,yVal]}
                                                                    rowsData.update(restOfWord)
                                                                    lineBreakFlag=0
                                                             else:
                                                                 
                                                                 wordInfo={wordId:[lastWordofLine,xVal,yVal,x_list[-1]]}
                                                                 rowsData.update(wordInfo)
                                                                 lineBreakFlag=0
                                                             
                                                             
                                                      else:
                                                         wordList.update(wordVal)
                                                         
                                                         # print(wordVal)
                                                     
                                         if(lineBreakFlag==1):
                                             rows.append(rowsData)
                                             
                                         if(wordId=="100"):
                                             rows.append(wordVal)
                                             rowInnerIndex=1
                                         if(current_y_diff<.001 and current_x_diff > .001):
                                             print(lineBreakFlag)
                                            
                                             #singleRow[rowInnerIndex]={rowsIndex:lastWordofLine}
                                             #rowsData.update(singleRow)
                                             
                                             # print(lastWordofLine)
                                             print('\n')
                                            
                                             
                                                  
                                                 
                                                  
                                                  
                                                      
                                                  
                                                 
                                                 
                     #print(i,'\n')
                                     
                     #blocks_page=page_content[0]['blocks']
    
           
print("end")  
    
        


    