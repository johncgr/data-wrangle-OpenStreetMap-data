# -*- coding: utf-8 -*-
"""
Created on Tue Feb 24 13:34:26 2015

@author: john
"""
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 24 13:32:26 2015

@author: marthaalexander
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import pprint
import re
import codecs
import json
"""
Your task is to wrangle the data and transform the shape of the data
into the model we mentioned earlier. The output should be a list of dictionaries
that look like this:

{
"id": "2406124091",
"type: "node",
"visible":"true",
"created": {
          "version":"2",
          "changeset":"17206049",
          "timestamp":"2013-08-03T16:43:42Z",
          "user":"linuxUser16",
          "uid":"1219059"
        },
"pos": [41.9757030, -87.6921867],
"address": {
          "housenumber": "5157",
          "postcode": "60625",
          "street": "North Lincoln Ave"
        },
"amenity": "restaurant",
"cuisine": "mexican",
"name": "La Cabana De Don Luis",
"phone": "1 (773)-271-5176"
}

You have to complete the function 'shape_element'.
We have provided a function that will parse the map file, and call the function with the element
as an argument. You should return a dictionary, containing the shaped data for that element.
We have also provided a way to save the data in a file, so that you could use
mongoimport later on to import the shaped data into MongoDB. 

Note that in this exercise we do not use the 'update street name' procedures
you worked on in the previous exercise. If you are using this code in your final
project, you are strongly encouraged to use the code from previous exercise to 
update the street names before you save them to JSON. 

In particular the following things should be done:
- you should process only 2 types of top level tags: "node" and "way"
- all attributes of "node" and "way" should be turned into regular key/value pairs, except:
    - attributes in the CREATED array should be added under a key "created"
    - attributes for latitude and longitude should be added to a "pos" array,
      for use in geospacial indexing. Make sure the values inside "pos" array are floats
      and not strings. 
- if second level tag "k" value contains problematic characters, it should be ignored
- if second level tag "k" value starts with "addr:", it should be added to a dictionary "address"
- if second level tag "k" value does not start with "addr:", but contains ":", you can process it
  same as any other tag.
- if there is a second ":" that separates the type/direction of a street,
  the tag should be ignored, for example:

<tag k="addr:housenumber" v="5158"/>
<tag k="addr:street" v="North Lincoln Avenue"/>
<tag k="addr:street:name" v="Lincoln"/>
<tag k="addr:street:prefix" v="North"/>
<tag k="addr:street:type" v="Avenue"/>
<tag k="amenity" v="pharmacy"/>

  should be turned into:

{...
"address": {
    "housenumber": 5158,
    "street": "North Lincoln Avenue"
}
"amenity": "pharmacy",
...
}

- for "way" specifically:

  <nd ref="305896090"/>
  <nd ref="1719825889"/>

should be turned into
"node_refs": ["305896090", "1719825889"]
"""


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Circle", "Plaza", "Terrace"]
            
suffix_mapping = {'st': "Street",
           'St': "Street",
           'st.': "Street",
           'St.': "Street",
           'Sreet' : "Street",
           'Ave': "Avenue",
           'Ave.': "Avenue",
           'ave' : "Avenue",
           'ave.': "Avenue",
           'Dfw' : 'DFW',
           'Ln' : 'Lane',
           'ln' : 'Lane',
           'Ln.' : 'Lane',
           'ln.' : 'Lane',
           'lane': 'lane',
           'exit' : 'Exit',
           'ct.' : 'Court',
           'ct' : 'Court',
           'court': 'Court',
           'Ct.' : 'Court',
           'Ct' : 'Court',
           'blvd' : 'Boulevard',
           'Dr.' : 'Drive',
           'Dr' : 'Drive',
           'Driv' : 'Drive',
           'path' : 'Path',
           'Pkwy' : 'Parkway',
           'Pky' : 'Parkway',
           'Pwy' : 'Parkway',
           'Pl' : 'Plaza',
           'Rd' : 'Road',
           'Roadd' : 'Road',
           'Ter.' : 'Terrace',
           'Tr' : 'Trail'
           }
           
prefix_mapping = { 's': 'South',
                   'n': 'North',
                   'w': 'West',
                   'e': 'East',
                   's.': 'South',
                   'n.': 'North',
                   'w.': 'West',
                   'e.': 'East',
                   'S': 'South',
                   'N': 'North',
                   'W': 'West',
                   'E': 'East', 
                   'S.': 'South',
                   'N.': 'North',
                   'W.': 'West',
                   'E.': 'East',
                   'sw': 'South West',
                   'se': 'South East',
                   'nw': 'North West',
                   'ne': 'North East',
                   'SW': 'South West',
                   'SE': 'South East',
                   'NW': 'North West',
                   'NE': 'North East',
                   'SW.': 'South West',
                   'SE.': 'South East',
                   'NW.': 'North West',
                   'NE.': 'North East',
                   's.w.': 'South West',
                   's.e.': 'South East',
                   'n.w.': 'North West',
                   'n.e.': 'North East',
                   'S.W.': 'South West',
                   'S.E.': 'South East',
                   'N.W.': 'North West',
                   'N.E.': 'North East',
                   'sw.': 'South West',
                   'se.': 'South East',
                   'nw.': 'North West',
                   'ne.': 'North East',
                   'SW.': 'South West',
                   'SE.': 'South East',
                   'NW.': 'North West',
                   'NE.': 'North East',
                   'Sw': 'South West',
                   'Se': 'South East',
                   'Nw': 'North West',
                   'Ne': 'North East',
                   'S.w.': 'South West',
                   'S.e.': 'South East',
                   'N.w.': 'North West',
                   'N.e.': 'North East',
                   }
                   
def update_postcode(postcode):
    postcode_re = re.compile(r'([0-9]{5})')
    postcode_m = re.search(postcode_re, postcode)
    if postcode_m:
        postcode = postcode_m.group()
            
    return postcode        
                      
                      
def update_suffix(name, mapping):
    
    #calling the street or avenue, etc part of address the suffix
    suffix_re = re.compile(r'(\w+\.?)$', re.IGNORECASE) 
    m = re.search(suffix_re, name)
    if m == False:
        return name   
    try:    
        if m.group() in mapping.keys():    
            def repl(m):
                output = mapping[m.group()]
                return output        
            new_name = re.sub(suffix_re, repl(m), name)       
            return new_name
        else:
            return name
    except AttributeError:
        return name
        
def update_prefix(name, mapping):
    
    #calling the cardinal prefix
    prefix_re = re.compile(r'^(\w\.?\w?\.?)', re.IGNORECASE) 
    m = re.search(prefix_re, name)
    if m == False:
        return name   
    try:    
        if m.group() in mapping.keys():    
            def repl(m):
                output = mapping[m.group()]
                return output        
            new_name = re.sub(prefix_re, repl(m), name)       
            return new_name
        else:
            return name
    except AttributeError:
        return name        
        
def speed_fixer(string):
    mph_pattern = re.compile(r'mph')
    speed_pattern = re.compile(r'(\A\d\d)')    
    if  re.search(mph_pattern, string) == None:
        speed_m = re.search(speed_pattern, string)
        speed = speed_m.group()
        fixed_speed = speed + ' mph'
        return fixed_speed
    else:
        return string
            

def array_maker(string):
    if string.find(':') != -1:
        string = string.split(':')
    elif string.find(';') != -1:
        string = string.split(';')   
    return string    

def shape_element(element):
    node = {}
    #working dictionary made from attributes of current element
    wd = {}
    #working dictionary for secondary level tags
    sd = {}
    
    if element.tag == "node" or element.tag == "way":
        wd = element.attrib
        
        try:
            node['id'] = wd['id']
        except KeyError:
            pass
        
        try:
            node['type'] = element.tag
        except KeyError:
            pass
        
        try:
            node['visible'] = wd['visible']
        except KeyError:
            pass
        
        #set values for pos array
        try:
            node['pos'] = [float(wd['lat']), float(wd['lon'])]
        except KeyError:
            pass
        
        #set values for created key
        try:
            node['created'] = {}
            for word in CREATED:
                node['created'][word] = wd[word]
        except KeyError:
            pass
        
        #begin evaluation of secondary tags
        #this really iterates over every element, not the children, but it seems to work
        for child in element.findall('./*'):
            
            #if tag is special case <nd>
            if child.tag == 'nd':
                try:
                    sd = child.attrib
                    node['node_refs'].append(sd['ref'])
                except KeyError:
                    node['node_refs'] = []
                    node['node_refs'].append(sd['ref'])
                sd = {}
                
            #set values for <tag>   
            if child.tag == 'tag':
                #create secondary working dictionary
                sd = child.attrib
                #call name cleaning function
                if sd['v']:
                    updated = update_suffix(sd['v'], suffix_mapping)
                    updated = update_prefix(updated, prefix_mapping)
                    child.set('v', updated)
                #post code cleaning function
                if sd['k'] == 'addr:postcode':
                    child.set('v', update_postcode(sd['v']))                   
                #check if tag has addr: info and no extra colons
                if sd['k'].startswith("addr:"):
                    if sd['k'].count(":") <= 1:
                            try:
                                node['address'][(sd['k'][5:])] = sd['v']
                            except KeyError:
                                node['address'] = {}
                                node['address'][(sd['k'][5:])] = sd['v']
                #shape tiger data
                elif sd['k'].startswith("tiger:"):
                    if sd['k'] == 'tiger:county' or sd['k'] == 'tiger:cfcc':
                        try:
                            node['tiger'][(sd['k'][6:])] = array_maker(sd['v'])
                        except KeyError:
                            node['tiger'] = {}
                            node['tiger'][(sd['k'][6:])] = array_maker(sd['v'])                          
                    else:        
                        try:
                            node['tiger'][(sd['k'][6:])] = sd['v']
                        except KeyError:
                            node['tiger'] = {}
                            node['tiger'][(sd['k'][6:])] = sd['v']
                #shape gnis data
                elif sd['k'].startswith("gnis:"):
                        try:
                            node['gnis'][(sd['k'][5:])] = sd['v']
                        except KeyError:
                            node['gnis'] = {}
                            node['gnis'][(sd['k'][5:])] = sd['v']                            
                        
                       
                else:
                    #fix known missing unit designations on speed
                    if sd['k'] == 'maxspeed':
                        node[sd['k']] = speed_fixer(sd['v'])
                    else:
                        node[sd['k']] = sd['v']
                
        #note that node can be a way, this is a bad variable name           
        return node                        
                                                   
    else:
        return None



def process_map(file_in, pretty = True):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data


data = process_map(r'/home/john/project/tarrant_county.osm')

with open(r'/home/john/project/logs/test2_json.txt', 'w') as fo:
    fo.write(str(data))


