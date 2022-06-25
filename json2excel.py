#!/usr/bin/python3
import sys, getopt
import subprocess
import time
import unicodedata
import string
import xlwt
import xlrd
import json as json
import os.path
from os import path

InterfaceList = []
EntityList = []
SystemList = []

def getHeader(itemList):
    headers = []
    for item in itemList:
        for head in [*item]:
            headers.append(head)
    return list(dict.fromkeys(headers))

def writeExcel(workbook, Sheet, List):
    headers = getHeader(List)
    sheet = workbook.add_sheet(Sheet)

    x = 0
    for header in headers:
        sheet.write(0, x, header)
        x+=1

    y = 1
    for item in List:
        x = 0
        for header in headers:
            try:
                value = item[header]
                sheet.write(y, x, value)
            except:
                pass
            x+=1
        y+=1

    #for index, value in enumerate(data):
    #    sheet.write(0, index, value)

    
   
def main(argv):
    fn = "switches.json"
    
    
    GlobalList = []
    if path.exists(fn):
        with open(fn, 'r') as f:
            GlobalList = json.load(f)

        sl = []
        il = []
        el = []
        for switch in GlobalList:
            sl.append(switch['System'])
            il.append(switch['Interfaces'])
            el.append(switch['Entities'])
            
        for systems in sl:
            for system in systems:
                SystemList.append(system)
        print(str(len(SystemList)) + " systems in database")
        
        for interfaces in il:
            for interface in interfaces:
                InterfaceList.append(interface)
        print(str(len(InterfaceList)) + " interfaces in database")

     
        for entities in el:
            for entity in entities:
                EntityList.append(entity)
        print(str(len(EntityList)) + " entities in database")

           
        workbook = xlwt.Workbook()
        writeExcel(workbook, 'Systems', SystemList)
        writeExcel(workbook, 'Interfaces', InterfaceList)
        writeExcel(workbook, 'Entities', EntityList)
        workbook.save("switches.xls")
        
    sys.exit(0)
    
if __name__ == "__main__":
    main(sys.argv[1:])
else:
    sys.exit(-1)

