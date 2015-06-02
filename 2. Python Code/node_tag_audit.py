# -*- coding: utf-8 -*-
"""
Created on Wed Feb 25 09:41:27 2015

@author: john
"""
import xml.etree.ElementTree as ET
import time
import re

#time of program start
start = time.time()

#error logging function
def add_error(log, key, error_msg):
    if key in log:
        log[key].append(error_msg)
    else:
        log[key] = [error_msg]

#tag audit
def tiger_audit(child, parent_element):
    e_att = parent_element.attrib
    counties = {'Tarrant, TX', 'Wise, TX', 'Denton, TX', 'Dallas, TX', 'Johnson, TX', 'Parker, TX'}
    #produce list of name_type add as entry to summary log
    if child.get('k') == "tiger:name_type":
        add_error(tiger_name_type_log, e_att['id'], child.get('v'))
    #could run into problems with this throwing errors when zips have the suffix    
    if ( child.get('k') == "tiger:zip_left"
         or child.get('k') == "tiger:zip_right" ):
             if len(child.get('v')) != 5:
                 add_error(error_log, e_att['id'], 'tiger:zip is not of correct length')
    #if zip code not in list of possible zip codes 
             if child.get('k') not in zips:
                 add_error(error_log, e_att['id'], 'tiger:zip is not in list of possible zips')
    #check tiger:county for possible county
    #if you see errors may need to regex parse this out to get at counties
    if child.get('k') == 'tiger:county':
        if child.get('v') not in counties:
            add_error(error_log, e_att['id'], 'tiger:county not one of possible counties')
    #check that tiger:cfcc is in correct format
    if child.get('k') == 'tiger:cfcc':
        cfcc_pattern = re.compile(r'^[a-zA-Z]\d\d$')
        if re.search(cfcc_pattern, child.get('v')) == None:
            add_error(error_log, e_att['id'], 'cfcc not in correct format')

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
            add_error(error_log, e_att['id'], missing_msg)
        #show extraneous tags
        extraneous = c_set - t_set
        if len(extraneous) != 0:
            extraneous_msg = 'child <tag> has extra attribute(s) ' + str(extraneous)
            add_error(error_log, e_att['id'], extraneous_msg)
    
    #addr:postcode audit
    if child.get('k') == 'addr:postcode':
        if child.get('v') not in zips:
            add_error(error_log, e_att['id'], str(child.get('v')))
        
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
                    add_error(error_log, e_att['id'], 'listed maxspeed is greater than 85 m.p.h')
                if  re.search(mph_pattern, child.get('v')) == None:
                    print(child.get('v'))
                    add_error(error_log, e_att['id'],
                          'maxspeed not in mph or is missing unit designation ')
    except KeyError:
        pass

    return None         

############Main Program###########
error_log = {}
node_ids = []
summary_log = {}
tiger_name_type_log = {}
minlat = 32.548
maxlat = 32.996
minlon = -97.5497
maxlon = -97.0319
zips = ['75052','75051', '76034', '76103','76248', '76262', '76001', '76002', '76003', '76004', '76005', '76006', '76007', '76010', '76011', '76012', '76013', '76014', '76015', '76016', '76017', '76018', '76019', '76094', '76096', '76020', '76197', '76198', '76021', '76022', '76095', '76109', '76116', '76126', '76132', '76131', '76191', '76166', '76177', '76034', '76195', '76036', '76016', '76039', '76040', '76140', '76193', '76119', '76140', '76101', '76102', '76103', '76104', '76105', '76106', '76107', '76108', '76109', '76110', '76111', '76112', '76113', '76114', '76115', '76116', '76117', '76118', '76119', '76120', '76121', '76122', '76123', '76124', '76126', '76127', '76129', '76130', '76131', '76132', '76133', '76134', '76135', '76136', '76137', '76140', '76147', '76148', '76150', '76155', '76161', '76162', '76163', '76164', '76166', '76177', '76179', '76180', '76181', '76182', '76185', '76191', '76192', '76193', '76195', '76196', '76197', '76198', '76199', '76244', '76051', '76092', '76099', '76111', '76117', '76137', '76148', '76180', '76052', '76053', '76054', '76244', '76248', '76060', '76192', '76135', '76136', '76108', '76135', '76063', '76127', '76127', '76118', '76180', '76182', '76118', '76180', '76182', '76180', '76114', '76013', '76015', '76020', '76118', '76180', '76118', '76180', '76114', '76131', '76179', '76114', '76092', '76115', '76122', '76196', '76129', '76130', '76019', '76019', '76137', '76148', '76107', '76114', '76108']
#path of file to be parsed
filein = r'/home/john/project/tarrant_county.osm'
for event, el in ET.iterparse(filein):
    if el.tag == 'node':
        for child in el.findall('./*'):
                tag_audit(child, el)
                

            
            
print(time.time() - start)
print(error_log)
#print(error_log)
  
with open(r'/home/john/project/logs/node_tag_audit_error_log.txt', 'w') as fileout:
    fileout.write(str(error_log))
    
with open(r'/home/john/project/logs/node_tag_audit_tiger_name_type_log.txt', 'w') as fileout:
    fileout.write(str(tiger_name_type_log))    

with open(r'/home/john/project/logs/node_tag_audit_summary_log.txt', 'w') as fileout:
    fileout.write(str(error_log))