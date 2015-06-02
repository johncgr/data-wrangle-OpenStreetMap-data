# -*- coding: utf-8 -*-
"""
Created on Wed Feb 25 08:46:32 2015

@author: john
"""
import xml.etree.ElementTree as ET
import time

#time of program start
start = time.time()

############Main Program###########
error_log = {}
way_ids = []
node_ids = []
minlat = 32.548
maxlat = 32.996
minlon = -97.5497
maxlon = -97.0319


#path of file to be parsed
filein = r'/home/john/project/tarrant_county.osm'

###nodes###
for event, el in ET.iterparse(filein):
    if el.tag == 'node':
        node_ids.append(el.get('id'))

node_ids_set = set(node_ids)
if len(node_ids) != len(node_ids_set):
    print(len(node_ids),len(node_ids_set))
    print('we have a nodes problem')        
            
with open(r'/home/john/project/logs/node_ids_list.txt', 'w') as fileout:
    node_ids.sort()
    s = str(node_ids)
    fileout.write(s)

###ways###
for event, el in ET.iterparse(filein):
    if el.tag == 'way':
        way_ids.append(el.get('id'))

way_ids_set = set(way_ids)
if len(way_ids) != len(way_ids_set):
    print(len(way_ids),len(way_ids_set))
    print('we have a way problem')        
            
with open(r'/home/john/project/logs/way_ids_list.txt', 'w') as fileout:
    node_ids.sort()
    s = str(node_ids)
    fileout.write(s)
    
print(time.time() - start)    