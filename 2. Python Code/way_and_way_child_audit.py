# -*- coding: utf-8 -*-
"""
Created on Wed Feb 25 12:14:02 2015

@author: john
"""
import xml.etree.ElementTree as ET
import time
import re
import pprint

#time of program start
start = time.time()

#error logging function
def add_error(log, key, error_msg):
    if key in log:
        log[key].append(error_msg)
    else:
        log[key] = [error_msg]

def nd_audit(child, parent_element):
    e_att = parent_element.attrib
    #make more specific in version 2
    c_dict = child.attrib
    #python 3.X returns a dictionar view item so must force into list()
    c_keys = list(c_dict.keys())
    if c_keys != ['ref']:
        add_error(nd_error_log, e_att['id'], 'problems with nd element' )
    ###code for check that nodes referenced by ways are in dataset    
    #else:
        #if c_dict['ref'] not in node_ids:
            #add_error(error_log, e_att['id'], 'way references node that is not in dataset')
        
def way_audit(element):
    e_att = element.attrib
    #node has required attributes
    req_el = set(['id', 'visible', 'version', 'changeset', 'timestamp',
                  'user','uid'])
    #flag nodes that do not have required keys
    way_set = set(e_att.keys())
    if way_set >= req_el == False:
        add_error(way_error_log, e_att['id'], 
                  'way does not have minimum required attributes')

#tag audit
def tiger_audit(child, parent_element):
    e_att = parent_element.attrib
    counties = {'Tarrant, TX', 'Ellis, TX', 'Wise, TX', 'Denton, TX', 'Dallas, TX', 'Johnson, TX', 'Parker, TX'}
    #produce list of name_type add as entry to summary log
    if child.get('k') == "tiger:name_type":
        add_error(tiger_name_type_log, e_att['id'], child.get('v'))
    #could run into problems with this throwing errors when zips have the suffix    
    if ( child.get('k') == "tiger:zip_left"
         or child.get('k') == "tiger:zip_right" ):
             if len(child.get('v')) != 5:
                 add_error(way_childtag_error_log, e_att['id'], 'tiger:zip is not of correct length')
    #if zip code not in list of possible zip codes 
        #add code here
    #check tiger:county for possible county
    #if you see errors may need to regex parse this out to get at counties
    if child.get('k') == 'tiger:county':
        if child.get('v') not in counties:
            msg = 'incorrect county' + str(child.get('v'))
            add_error(way_childtag_error_log, e_att['id'], msg)
    #check that tiger:cfcc is in correct format
    if child.get('k') == 'tiger:cfcc':
        cfcc_pattern = re.compile(r'^[a-zA-Z]\d\d$')
        if re.search(cfcc_pattern, child.get('v')) == None:
            msg = 'incorrect cfcc format' + str(child.get('v'))
            add_error(way_childtag_error_log, e_att['id'], msg)

def tiger_name_crosscheck(child, tag_name):
    #change this in second version to actually crosscheck the fields instead
    #of creating a log
    #tiger:name_base
    if child.get('k') == 'tiger:name_base':
        add_error(summary_log, 'tiger:name_base', child.get('v'))
    #tiger name_type
    if child.get('k') == 'tiger:name_type':
        add_error(summary_log, 'tiger:name_type', child.get('v'))        
    #tiger name_direction_prefix
    if child.get('k') == 'tiger:name_direction_prefix':
        add_error(summary_log, 'tiger:name_direction_preix', child.get('v'))        
    #tiger name_direction_suffix
    if child.get('k') == 'tiger:name_direction_suffix':
        add_error(summary_log, 'tiger:name_direction_suffix', child.get('v'))        
               
                      
def tag_audit(child, parent_element):
    e_att = parent_element.attrib
    #scan for extraneous or missing attributes
    if child.attrib.keys() != ['k', 'v']:
        #show missing tags
        c_set = set(child.attrib.keys())
        t_set = set(['k', 'v'])
        missing = t_set - c_set
        if len(missing) != 0:
            missing_msg = 'child <tag> is missing attribute ' + str(missing)
            add_error(way_childtag_error_log, e_att['id'], missing_msg)
        #show extraneous tags
        extraneous = c_set - t_set
        if len(extraneous) != 0:
            extraneous_msg = 'child <tag> has extra attribute(s) ' + str(extraneous)
            add_error(way_childtag_error_log, e_att['id'], extraneous_msg)
            
    #tiger audit
    if child.get('k'):        
        if child.get('k').startswith('tiger') == True:
            tiger_audit(child, parent_element)
    #extract tag k:name value, if present
    if child.get('k') == 'name':
        tag_name = child.get('v')
        tiger_name_crosscheck(child, tag_name)
        
    #bounds check maxspeed (should only be in <ways>) 
    #also check for unit of mph        
    try:
        if child.get('k') == 'maxspeed':
            speed_pattern = re.compile(r'(\A\d\d)')
            mph_pattern = re.compile(r'mph')
            speed = re.match(speed_pattern, child.get('v'))
            if speed:
                speed = float(speed.group())
                if speed > 85:
                    add_error(way_childtag_error_log, e_att['id'], 'listed maxspeed is greater than 85 m.p.h')
                if  re.search(mph_pattern, child.get('v')) == None:
                    print(child.get('v'))
                    add_error(way_childtag_error_log, e_att['id'],
                          'maxspeed not in mph or is missing unit designation ')
    except KeyError:
        pass

    return None         




############Main Program###########
way_error_log = {}
summary_log = {}
tiger_name_type_log = {}
way_childtag_error_log = {}
nd_error_log = {}
minlat = 32.548
maxlat = 32.996
minlon = -97.5497
maxlon = -97.0319

#path of file to be parsed
filein = r'/home/john/project/tarrant_county.osm'
for event, el in ET.iterparse(filein):
    if el.tag == 'way':
        way_audit(el)
        for child in el.findall('./tag'):
            tag_audit(child, el)
        for child in el.findall('./nd'):
            nd_audit(child, el)

                    
#for x in range(50):
   # pprint.pprint(way_childtag_error_log)            
            
print(time.time() - start)
#print(way_error_log)
#print(way_childtag_error_log)
print(nd_error_log)
  
with open(r'/home/john/project/logs/way_error_log.txt', 'w') as fileout:
    fileout.write(str(way_error_log))

with open(r'/home/john/project/logs/way_childtag_error_log.txt', 'w') as fileout:
    fileout.write(str(way_childtag_error_log))

with open(r'/home/john/project/logs/way_childnd_error_log.txt', 'w') as fileout:
    fileout.write(str(nd_error_log))    