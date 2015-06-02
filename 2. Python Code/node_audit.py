# -*- coding: utf-8 -*-
"""
Created on Wed Feb 25 08:17:38 2015

@author: john
"""
import xml.etree.ElementTree as ET
import time
import re

#time of program start
start = time.time()

#counter
counter = 0

#error logging function
def add_error(log, key, error_msg):
    if key in log:
        log[key].append(error_msg)
    else:
        log[key] = [error_msg]

#node audit
def node_audit(element, minlat, maxlat, minlon, maxlon):
    e_att = element.attrib
    #list of a node's required attributes
    req_el = set(['id', 'visible', 'version', 'changeset', 'timestamp',
                  'user','uid', 'lat', 'lon'])
    #flag nodes that do not have required keys
    node_set = set(e_att.keys())
    if node_set >= req_el == False:
        add_error(error_log, e_att['id'], 
                  'node does not have minimum required attributes')
    #check that lat and long both hav 7 digits after the decimal
    pattern = re.compile(r'\.\d{7}')
    lat_result = re.search(pattern, e_att['lat'])
    lon_result = re.search(pattern, e_att['lon'])
    if lat_result == None or lon_result == None:
        add_error(error_log, e_att['id'], 
                  'lat or lon not of specified precision')
    #bounds check lat and long
    #wiggle room is acceptable imprecision for reporting GPS out of bonds
    #errors 
    #at 34 deg N 0.0000001 is about 9 mm
    # 0.01 is about 900 m              
    wiggle_room = 0.01              
    try:              
        lat = float(e_att['lat'])
        lon = float(e_att['lon'])             
        if lat < minlat:
            latdif = minlat - lat
            if latdif > wiggle_room:
                add_error(error_log, e_att['id'],
                'node lat is south of boundary area by '+ str(latdif) + str(lat))
        if lat > maxlat:
            latdif = lat - maxlat
            if latdif > wiggle_room:
                add_error(error_log, e_att['id'],
                'node lat is north of boundary area by ' + str(latdif) + str(lat))
        #note the maxlon is eastmost line of area
        if lon > 0:
            add_error(error_log, e_att['id'],
                'node lon is wrong hemisphere or missing neg(-) sign ')
        if lon < minlon:
            londif = minlon - lon
            if londif > wiggle_room:
                add_error(error_log, e_att['id'],
                'node lon is west of boundary area by ' +str(londif) + str(lon))
        if lon > maxlon:
            londif = lon - maxlon
            if londif > wiggle_room:
                add_error(error_log, e_att['id'],
                'node lon is east of boundary area by ' + str(londif) + str(lon))             
    except ValueError:
        add_error(error_log, e_att['id'],'either lat or lon is missing')
        
    return None         

############Main Program###########
error_log = {}
minlat = 32.548
maxlat = 32.996
minlon = -97.5497
maxlon = -97.0319
#path of file to be parsed
filein = r'/home/john/project/tarrant_county.osm'
for event, el in ET.iterparse(filein):
    if el.tag == 'node':
        node_audit(el, minlat, maxlat, minlon, maxlon)
            
print(time.time() - start)
print(len(error_log))
#print(error_log)
  
#with open(r'/home/john/project/logs/node_audit_1.txt', 'w') as fileout:
    #fileout.write(str(error_log))