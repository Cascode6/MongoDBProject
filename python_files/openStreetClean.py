#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
from collections import defaultdict

#code taken largely from Udacity MongoDB course problems and adjusted to clean Open Street Map data found in buffalogrove.xml
#adjustments by Casey Faist 1/13/16
#Note: Project reworked in Python 3, rather than 2 as in lessons.

MAPFILE = 'buffalogrove.osm'

## checking in with the data: what's there, how much, general stuff
#From 6.1
def count_tags(filename): #returns the numbers and names of different tags in document
	tags = {}
	for event, elem in ET.iterparse(filename):
		tag = elem.tag
		tags[tag] = tags.get(tag, 0) + 1
	return tags


##From 6.3
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
		
def key_type(element, keys): # returns the number of problematic keys in the dataset
    if element.tag == "tag":
        # YOUR CODE HERE
        k = element.attrib['k']
        if re.search(lower,k):
            keys['lower'] +=1
        elif re.search(lower_colon,k):
            keys['lower_colon'] +=1
        elif re.search(problemchars,k):
            keys['problemchars'] +=1
        else:
            keys['other'] += 1
        
    return keys


def char_types(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys


#From 6.4
def get_user(element):
    uid = element.attrib['uid']
    return uid


def process_users(filename): #changed from process_map to _users to avoid conflict
    users = set()
    for event, element in ET.iterparse(filename):
        if 'uid' in element.attrib:
            uid = get_user(element)
            if uid not in users:
                users.add(uid)
            else: 
                pass
    return users

# from 6.5 -- cleaning street names & building JSON file
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
name_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

###The following regex expression is taken directly from http://www.diveintopython.net/regular_expressions/phone_numbers.html,
###Selected for robustness in dealing with different phone number formats. All comments come from the page as well; I kept them for my own studying purposes.
phone_type_re = re.compile(r'''
                # don't match beginning of string, number can start anywhere
    (\d{3})     # area code is 3 digits (e.g. '800')
    \D*         # optional separator is any number of non-digits
    (\d{3})     # trunk is 3 digits (e.g. '555')
    \D*         # optional separator
    (\d{4})     # rest of number is 4 digits (e.g. '1212')
    \D*         # optional separator
    (\d*)       # extension is optional and can be any number of digits
    $           # end of string
    ''', re.VERBOSE)

#expected values used in audits
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]

expected_places = ["Target", "Walgreens", "Subway", "Walmart"]
expected_amenities = []
expected_nums = []
expected_counties = ["Lake", "Cook"]

#mapping dictionaries for fix_name function, created after audits
street_mapping = {"St": "Street",
           "st": "Street",
           "Dr": "Drive",
           "Ave": "Avenue",
           "Blvd": "Boulevard",
           "Ct": "Court",
           "Hwy": "Highway",
           "N": "North",
           "S" : "South",
           "E" : "East",
           "W": "West",
           "west": "West",
           "West": "West",
           "Rd": "Road",
           "road": "Road",
           "main": "Main",
           "cuba": "Cuba",
           "rand": "Rand",
           "pfingsten" : "Pfingsten",
           "lane": "Lane",
           }


place_mapping = {"headquarters":"Headquarters",
                 "road": "Road",
                 "W": "West",
                 "Cir": "Circle",
                 "St": "St.", ###For further study: How to regex decipher "Saint" vs "Street"?
                 "Rd": "Road",
                 "Pl" : "Place",
                 "N" : "North",
                 "Drove": "Drive",
                 "Driv": "Drive",
                 "Dr": "Drive",
                 "Dept": "Department",
                 "Ct": "Court",
                 "Chilis": "Chili's",
                 "Blvd":"Boulevard",
                 "Barrinton":"Barrington",
                 "Aveue": "Avenue",
                 "Ave": "Avenue",
                 "Street;West": "Street, West",
                 "noodles&company": "Noodles & Company",
                 "house": "House",
                 "ramp": "Ramp",
                 "theater": "Theater",
                 "tires": "Tires",
                 "Lextington": "Lexington",
                 "line": "Line",
                 "pawtucket": "Pawtucket",
                 "tynsborough": "Tynsborough",
                 "blvd": "Boulevard",
                 "court": "Court",
                 "courts": "Courts",
                 "barnhouse": "Barnhouse",
                 "ma": "MA",
                 }

amenity_mapping = {"arts_centre":"arts center",
                   "bar;restaurant":"bar/restaurant",
                   "bicycle_parking":"bicycle parking",
                   "car_rental":"car rental",
                   "car_wash": "car wash",
                   "church_hall": "church hall",
                   "community_centre": "community center",
                   "department_store": "department store",
                   "drinking_water": "drinking water",
                   "exercise_facility": "exercise facility",
                   "fast_food": "fast food",
                   "fire_station": "fire station",
                   "grave_yard": "graveyard",
                   "nursing_home": "nursing home",
                   "parking_entrance":"parking entrance",
                   "place_of_worship":"place of worship",
                   "post_box":"postbox",
                   "post_office":"post office",
                   "public_building":"public building",
                   "swimming_pool":"swimming pool",
                    }


county_mapping = {"Cook,Illinois,Ill.,IL,USA":"Cook",
                  "IL":"",
                  "Lake,Illinois,Ill.,IL,USA":"Lake",
                  "Oriole Lane": ""
                  }

##note: no phone mapping needed, as .replace() was sufficient

#audits used to test and clean data
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)
            
def audit_name(name_types, place_name):
    m = name_type_re.search(place_name)          
    if m:
        name_type = m.group()
        if name_type not in expected_places:
            name_types[name_type].add(place_name)

def audit_amenity(amenity_types, amenity_name):
    m = name_type_re.search(amenity_name)          
    if m:
        amenity_type = m.group()
        if amenity_type not in expected_amenities:
            amenity_types[amenity_type].add(amenity_name)

def audit_phone(phone_types, phone_num):
    m = phone_type_re.search(phone_num)          
    if m:
        phone_type = m.group()
        if phone_type not in expected_nums:
            phone_types[phone_type].add(phone_num)

def audit_county(county_types, county):
    m = name_type_re.search(county)          
    if m:
        county_type = m.group()
        if county_type not in expected_counties:
            county_types[county_type].add(county)

#short functions for determining k attrib values

def is_name(elem):
    return (elem.attrib['k'] == "name")

def is_amenity(elem):
    return (elem.attrib['k'] == "amenity")

def is_phone(elem):
    return (elem.attrib['k'] == "phone")
    
def is_population(elem): ##found in dataset; as area is more than one county, might be useful info
    return (elem.attrib['k'] == "population")
    


##address fields
def is_address_part(elem):
    return (elem.attrib['k'] in ADDRESS)

def is_street_tag(elem):
    return (elem.attrib['k'] == "addr:street")

def is_housenum(elem):
    return (elem.attrib['k'] == "addr:housenumber" )
    
def is_postcode(elem):
    return (elem.attrib['k'] == "addr:postcode")

def is_county(elem): ##found in dataset; as area is more than one county, might be useful info
    return (elem.attrib['k'] == "is_in")
 




###

def audit(osmfile):
    osm_file = open(osmfile, "r")
    name_types = defaultdict(set)
    amenity_types = defaultdict(set)
    phone_types = defaultdict(set)
    county_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_name(tag):
                    audit_name(name_types, tag.attrib['v'])
                if is_amenity(tag):
                    audit_amenity(amenity_types, tag.attrib['v'])
                if is_phone(tag):
                    audit_phone(phone_types, tag.attrib['v'])
                if is_county(tag):
                    audit_county(county_types, tag.attrib['v'])
    return name_types, amenity_types, phone_types, county_types
    


def fix_name(name, mapping):
    
    for word in mapping.keys():
        W = r'\b' + word + r'\b\.?'
        R = mapping[word]
        name = re.sub(W, R, name)
    return name

def fix_num(num):
    m = phone_type_re.search(num)
    if m:
        num = num.replace("(", "").replace(")", "").replace('-', '.').replace('+', '').replace(' ', '.')
    
        return num
    else:
        pass

##6.6
CREATED = ['version', 'changeset', 'timestamp', 'user', 'uid'] #values to be put into nested "created" dictionary
ADDRESS = ['addr:housenumber', 'addr:postcode', 'addr:street'] #values to be put into nested "address" dictionary
   

def shape_element(element): ##forms json objects based on elements in the OSM file
    node = {}
    if element.tag == "node" or element.tag == "way" :
        node['type'] = element.tag
        for tag in element.attrib:
            if tag == 'id':
                    node['id'] = element.attrib['id']
            elif tag == 'visible':
                node['visible'] = element.attrib['visible']
            elif tag == 'lon' or tag == 'lat':
                if  'lon' in element.attrib and 'lat' in element.attrib:
                    latfloat = float(element.attrib['lat'])
                    lonfloat = float(element.attrib['lon'])
                    node['pos'] = [latfloat, lonfloat]
            else:
                pass
            
            if tag in CREATED: #nested "created" dictionary values
                node['created'] = {}
                if 'uid' in element.attrib:
                    node['created']['uid'] = element.attrib['uid']
                if 'user' in element.attrib:
                    node['created']['user'] = str(element.attrib['user'])
                if 'timestamp' in element.attrib:
                    node['created']['timestamp'] = element.attrib['timestamp']
                if 'changeset' in element.attrib:
                    node['created']['changeset'] = element.attrib['changeset']
                if 'version' in element.attrib:
                    node['created']['version'] = element.attrib['version']
                else:
                    pass
            else:
                pass
            
           
            
        
        for tag in element.iter("tag"):
            if is_amenity(tag):
                node['amenity'] = fix_name(tag.attrib['v'], amenity_mapping)
            if is_name(tag):
                node['name'] = fix_name(tag.attrib['v'], place_mapping)
            if is_phone(tag):
                node['phone'] = fix_num(tag.attrib['v'])
            if is_population(tag):
                node['population'] = int(tag.attrib['v'])
            else:
                pass
                    
            if is_address_part(tag): #separates child tags that go into nested "address" section
                if 'address' not in node: 
                    address = {"state": "Illinois",} #whole area is in illinois, so this is a given
                    node['address'] = {} 
                    
                else:
                    pass
                if is_housenum(tag):
                    address['housenumber'] = tag.attrib['v']
                    node['address'].update(address)
                    
                elif is_postcode(tag):
                    address['postcode'] = tag.attrib['v']
                    node['address'].update(address)
                    
                elif is_street_tag(tag):
                    address['street'] = fix_name(tag.attrib['v'], street_mapping)
                    node['address'].update(address)
                    
                elif is_county(tag):
                    address['county'] = fix_name(tag.attrib['v'], county_mapping)
                    node['address'].update(address)
                else:
                    pass
            else:
                pass
        
        if element.tag == "way":
            refnums = []
            for tag in element.iter("nd"):
                refnums.append(tag.attrib['ref'])
            node['node_refs'] = refnums
        
        if 'name' in node and 'population' in node:
            if node['name'] == 'Wheeling' and 'population' in node:
                node['population'] = 52039
        else:
            pass
        return node
        
    else:
        return None


#Iterate through XML and make data
def process_map(file_in):
    data = []
    for _, element in ET.iterparse(file_in):
        el = shape_element(element)
        if el:
            data.append(el)
    return data

jsondata = process_map(MAPFILE)

JSONFILE = 'buffalogrove.osm.json'

json.dump(jsondata, open(JSONFILE, 'w'))

