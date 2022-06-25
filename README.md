# get-switch-info
pull information out of your network switches using SNMP

## get-switch.py

`./get-switch.py -H  <hosts> -O <outputfile>`
  
`<hosts>` can be an IP address, a subnet, a list of addresses, a range or a file.
  The program first checks if the parameter exists as a file. if so. The syntax in a file is the same, but can be multiple lines long
  
  a few examples of host definitions:
  1. search a single host:
  * `192.168.1.1`
  * `10.0.0.30`
  
  2. search a list of hosts
  *  `"192.168.1.1, 192.168.1.30, 10.0.0.100"` 
  *  `10.10.10.10,10.11.12.13` 

  3. search a range:
  *  `10.15.0.0/30`    will make this a list of 10.15.0.0, 10.15.0.1, 10.15.0.2 and 10.15.0.3 
  *  `192.168.1.1/24`  will search the entire subnet of 255 IP addresses. This goes from 192.168.1.0 up to 192.168.1.255 and forgives you about the IP address not being the network address
  
  4. search a combination:
  * `192.168.0.1, 192.168.0.100-192.168.0.120, 10.0.50.128/25`

`<outputfile>` is the filename of the JSON file all the information will be written to. It automatically appends the `.json` extension to the file

### commandline examples
* `./get-switch.py -H  172.17.10.1 -O myswitch`
* `./get-switch.py -H  192.168.100.1,192.168.100.3 -O myswitches`
* `./get-switch.py -H  192.168.100.1,10.100.0.80-10.100.0.100 -O serverswitches`
* `./get-switch.py -H  "192.168.100.1, 10.100.0.80-10.100.0.100" -O network`
* `./get-switch.py -H  "10.0.100.0/24, 10.0.101.0/26, 10.0.101.100,10.0.101.104" -O all`


## json2excel.py
`./json2excel.py`
doesn't take parameters yet. i'm working on that
