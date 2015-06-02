# -*- coding: utf-8 -*-
"""
Created on Wed Feb 25 08:02:21 2015

@author: john
"""
import xml.etree.ElementTree as ET
import time

#time of program start
start = time.time()

#error logging function
def add_error(log, key, error_msg):
    if key in log:
        log[key].append(error_msg)
    else:
        log[key] = [error_msg]

#data auditing tasks common to nodes and ways
def common_tasks(element):
    e_att = element.attrib    
    #scan for strangely named elements
    #note there are meta, and member tags, ignore? when 
    osm_primitives = set(['node', 'way', 'relation'])
    if element.tag not in osm_primitives:
        print(element.tag)
        return None
        #add_error(error_log, e_att['id'], 
                  #'First Level Elemet not node way or relation ')
    #check that uid only contains numbers
    if unicode(e_att['uid']).isnumeric() == False:
        add_error(error_log, e_att['id'],
                  'uid contains non-numeric characters')
    #check if timestamp is valid YYYY-MM-DDThh:mm:ssTZD and bounds check
    try:
        time_tuple = time.strptime(e_att['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
        #bounds check
        if time_tuple[0] <= 2003:
            add_error(error_log, e_att['id'], 'timestamp before OSM launch date')
        if time_tuple[0] == 2004 and time_tuple[1] < 7:
            add_error(error_log, e_att['id'], 'timestamp before OSM launch date')        
    except ValueError:
        add_error(error_log, e_att['id'], 
                  'timestamp is not in correct format')
    #end common tasks
    return None

############Main Program###########
error_log = {}
#path of file to be parsed
filein = r'/home/john/project/tarrant_county.osm'
for event, el in ET.iterparse(filein):
    if el.tag in set(['tag', 'nd', 'osm', 'bounds', 'osm_base']):
        continue
    common_tasks(el)
    

print(time.time() - start)
print(error_log)
        