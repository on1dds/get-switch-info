#!/usr/bin/python3
#################################################################
## Author: Joachim Elen
## Date: 2022-06-25
## 
## Purpose: Read information out of network switches using SNMP
## and write them into a JSON file
##
#################################################################

import sys, getopt
import subprocess
import time
import unicodedata
import string
import json
import os.path
from os import path
from ipaddress import ip_address

RC_OK=0
RC_ERROR=1

SystemList = []
InterfaceList = []
EntityList = []
trunkList = []

VERBOSITY_LEVEL = 0
#################################################################
##
## SYSTEM
##
#################################################################
trunk_template = {
        'tag' : '',
        'ifIndex' : '',
        'status' : ''
    }
    
SysOIDs = {
    "base" : ".1.3.6.1.2.1.1",
    "sysName" : "%s.5.%s",
    "Location" : "%s.6.%s",
    "Contact" : "%s.4.%s"
}

#################################################################
##
## INTERFACES
##
#################################################################

Interface_OIDs1 = {
    "base" : ".1.3.6.1.2.1.2.2.1",
	"ifIndex" :"%s.1.%s",
	"Descr" :"%s.2.%s",
	"Type" :"%s.3.%s",
	"Mtu" :"%s.4.%s",
	"Speed" :"%s.5.%s",
	"PhysAddress" :"%s.6.%s",
	"AdminStatus" :"%s.7.%s",
	"OperStatus" :"%s.8.%s",
	"LastChange" :"%s.9.%s",
	"InOctets" :"%s.10.%s",
	"InUcastPkts" :"%s.11.%s",
	"InNUcastPkts" :"%s.12.%s",
	"InDiscards" :"%s.13.%s",
	"InErrors" :"%s.14.%s",
	"InUnknownProtos" :"%s.15.%s",
	"OutOctets" :"%s.16.%s",
	"OutUcastPkts" :"%s.17.%s",
	"OutNUcastPkts" :"%s.18.%s",
	"OutDiscards" :"%s.19.%s",
	"OutErrors" :"%s.20.%s",
	"OutQLen" :"%s.21.%s",
	# "Specific" :"%s.22.%s"
}
Interface_OIDs2 = {
    "base" : ".1.3.6.1.2.1.31.1.1.1",
    "Name" : "%s.1.%s",
    "HCInOctets" : "%s.6.%s",
    "HCOutOctets" : "%s.10.%s",
    "HighSpeed" : "%s.15.%s",
    "PromiscuousMode" : "%s.16.%s",
    "ConnectorPresent" : "%s.17.%s",
    "Alias" : "%s.18.%s",
}

#################################################################
##
## ENTITIES
##
#################################################################

Entity = {
    "sysName" : "",
    "host" : "",
    "Index" : ""
}

Entity_OIDs = {
    "base" : ".1.3.6.1.2.1.47.1.1.1.1",
    "Class" : "%s.5.%s",
    "Name" : "%s.7.%s",
    "ModelName" : "%s.13.%s",
    "Description" : "%s.2.%s",
    # "entVendorType" : "%s.3.%s",
    "ContainedIn" : "%s.4.%s",
    "ParentRelPos" : "%s.6.%s",
    "HardwareRev" : "%s.8.%s",
    "FirmwareRev" : "%s.9.%s",
    "SoftwareRev" : "%s.10.%s",
    "SerialNum" : "%s.11.%s",
    "MfgName" : "%s.12.%s",
    "isReplacable" : "%s.16.%s"
}

def p(v,s):
    if (v >= VERBOSITY_LEVEL): print(s)
    return
    
def setCR(s):
    out2 = ""
    quoted = False
    for c in s:
        if (c == '"'): quoted = not quoted
        if (quoted and c == '\n'): c = ','
        if (quoted and c == '\r'): c = ''
        
        out2 += c
    return out2

def get_snmpinfo(host, tagList, OIDList):
    base_oid = OIDList['base']
    PropList = [*OIDList]
    PropList.remove('base')
    
    cmd="snmpwalk " + host + " " + base_oid + " -Onq -t 1 -r 0"
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) 
    output, err = process.communicate()
    output=output.decode("utf-8")
    if (len(output) < 1):
        print ("  ERROR: Failed to find host or interface")
        sys.exit(RC_ERROR) 
        
    output = setCR(output)
    output = output.split('\n')

    for line in output:
        if(len(line) > 0):
            oid = line.split(' ')[0].strip()
            Index = oid.split('.')[-1].strip()
            val = line[len(oid):].replace('"','').strip()

            ent = []
            try:
                ent = next(item for item in tagList if item["Index"] == Index)       
            except:
                ent = Entity.copy()
                ent['host'] = host
                ent['Index'] = Index
                tagList.append(ent)
                
            for Prop in PropList:
                prop_oid = OIDList[Prop] % (base_oid, Index)
                #print("'" + prop_oid + "' ==> " + OIDList[Prop], base_oid, Index)
                
                if (oid == prop_oid):
                    ent[Prop] = val

def get_trunks(host, tagList):
    base_oid = ".1.3.6.1.2.1.31.1.2.1.3"
    cmd="snmpwalk " + host + " " + base_oid + " -Onq"
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) 
    output, err = process.communicate()
    output=output.decode("utf-8")
    if (len(output) < 1):
        print ("  ERROR: Failed to find host or interface")
        sys.exit(RC_ERROR) 
    
    output = setCR(output)
    output = output.split('\n')

    for line in output:
        oid = tag = port = val = ""
        if(len(line) > 0):
            oid = line.split(' ')[0].strip()
            tag = oid.split('.')[-2].strip()
            ifIndex = oid.split('.')[-1].strip()
            status = line[len(oid):].replace('"','').strip()
        trunk = trunk_template.copy()

        trunk['ifIndex'] = ifIndex
        trunk['status'] = status

        try:
            t2 = next(item for item in tagList if item["ifIndex"] == tag)  
            trunkName = t2['Name']
            trunk['tag'] = trunkName
            trunkList.append(trunk)
        except:
            pass


def get_options(param, argv):
    param.clear()
    param['host'] = ''
    param['file'] = ''
    try:
        opts, args = getopt.getopt(argv,"Vh:H:v:O:",["version","help","hostname=","verbose=","output="])
    except getopt.GetoptError:
        print_help()
        print("ERROR incorrect use of parameters")
        sys.exit(RC_ERROR)
    for opt, arg in opts:
        # VERSION
        if opt in ("-V","--version"):
            print_version()
            sys.exit (RC_OK) 
        
        # HELP
        elif opt in '-h':
            print_help()
            sys.exit (RC_OK) 
   

        # OUTPUT FILE
        elif opt in ("-O","--output"):
            param['file'] = arg + ".json"
            
        # HOSTNAME
        elif opt in ("-H","--hostname"):
            try:
                param['host'] = get_hostlist(arg)
            except:
                print("ERROR: syntax fault in host definition")
                sys.exit (RC_ERROR)
                
        # VERBOSE
        elif opt in ("-v","--verbose"):
            VERBOSITY_LEVEL = arg

    if (param['host'] == ""):
        print("ERROR: No hosts defined")
        sys.exit (RC_ERROR)         

    if (param['file'] == ""):
        print("ERROR: No output file defined")
        sys.exit (RC_ERROR)           
    return param

def ips(start, end):
    start_int = int(ip_address(start).packed.hex(), 16)
    end_int = int(ip_address(end).packed.hex(), 16)
    return [ip_address(ip).exploded for ip in range(start_int, end_int+1)]
 
def get_hostlist(hosts):
    outlist= []
    inlist = hosts
    if(type(hosts)==str):
        if(os.path.exists(hosts)):
            f = open(hosts, 'r')
            inlist = f.readlines()
            for host in inlist:
                if(',' in host):    
                    for h in host.split(','):
                        outlist.append(h.strip())
                else:
                    outlist.append(host.strip())
            inlist = outlist.copy()
            outlist.clear()
        else:
            inlist=[hosts]

    # REMOVE EMPTY ENTRIES
    for host in inlist:
        host = host.strip()
        if (len(host) > 0):
            outlist.append(host)
    
    inlist = outlist.copy()
    outlist.clear()

    # SPLIT COMMA SEPERATED LIST IN INDIVIDUAL ITEMS IN LIST
    for host in inlist:
        if(',' in host):    
            for h in host.split(','):
                outlist.append(h.strip())
        else:
            outlist.append(host.strip())
    inlist = outlist.copy()
    outlist.clear()

    # CONVERT SUBNETTED ITEMS TO INDIVIDUAL IPs
    for host in inlist:
        if('/' in host):
            hh = host.split('/')
            if(len(hh) == 2):
                h = host.split('/')
                start_int = int(ip_address(h[0]).packed.hex(), 16)
                cidr = int(h[1])
                start_int = start_int - start_int%2**(32-cidr)
                end_int = start_int + 2**(32-cidr)
                l=ips(start_int,end_int-1)
                for ip in l:
                    outlist.append(str(ip_address(ip)))
                    
            elif(len(hh) == 1):
                outlist.append(host.strip())
            else:
                print("ERROR in host list")
                sys.exit(RC_ERROR)         
        else:
            outlist.append(host.strip())
            
    inlist = outlist.copy()
    outlist.clear()
    
    for host in inlist:
        if('-' in host):
            hh = host.split('-')
            if(len(hh) == 2):
                h = host.split('-')
                start = h[0]
                end = h[1]
                l=ips(start,end)
                for ip in l:
                    outlist.append(ip.strip())
            elif(len(hh) == 1):
                outlist.append(host.strip())
            else:
                sys.exit(RC_ERROR)                 
        else:
            outlist.append(host.strip())

    inlist = outlist.copy()
    outlist.clear()

    for item in inlist:
        item_int = int(ip_address(item).packed.hex(), 16)
        outlist.append(item_int)
        
    inlist = list(dict.fromkeys(outlist))
    inlist.sort()
    outlist.clear()
    for item in inlist:
        outlist.append(str(ip_address(item)))
    return outlist
   
def main(argv):
    param = {}
    get_options(param, argv)
    
    hosts = param['host']
    
    for host in hosts:
        host = host.strip()
        print(host)
        SystemList.clear()
        InterfaceList.clear()
        EntityList.clear()
        trunkList.clear()
        try:
            print("  reading system ... ")
            get_snmpinfo(host,SystemList, SysOIDs)
            
            print("  reading interfaces ... ")
            get_snmpinfo(host,InterfaceList, Interface_OIDs1)
            get_snmpinfo(host,InterfaceList, Interface_OIDs2)
            
            print("  reading entitites ...")
            get_snmpinfo(host,EntityList, Entity_OIDs)

            print("  getting trunks ... ")
            get_trunks(host, InterfaceList)   

            for _iface in InterfaceList:
                _iface['Tags'] = ""
                idx = _iface['ifIndex']
                s=""
                for _trunk in trunkList:
                    if (_trunk['ifIndex'] == idx):
                        s = s + _trunk['tag'] + ","
                if(len(s) > 0): s = s[:-1]
                _iface['Tags'] = s
            
            sysName = SystemList[0]['sysName']
            
            for iface in InterfaceList:
                iface['sysName'] = sysName

            for ent in EntityList:
                ent['sysName'] = sysName

            print("  writing to file ...")
            GlobalList = {
                'sysName' : sysName,
                'System' : SystemList,
                'Interfaces' : InterfaceList,
                'Entities' : EntityList
            }

            importList = []
            switchList = []

            outfile=param['file']

            if path.exists(outfile):
                with open(outfile, 'r') as f:
                    importList = json.load(f)
            
            for switch in importList:
                if switch['sysName'] != sysName:
                    switchList.append(switch)
        
            switchList.append(GlobalList) 
            print(outfile)
            with open(outfile, 'w') as f:
                json.dump(switchList, f)
            print("  done")
        except:
            pass
 
 
    sys.exit(RC_OK)
    
if __name__ == "__main__":
    main(sys.argv[1:])
else:
    sys.exit(-1)
