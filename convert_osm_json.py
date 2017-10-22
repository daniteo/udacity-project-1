#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Prepare the OSM file from Belo Horizonte to a JSON format to be imported to MongoDB
"""
import xml.etree.cElementTree as ET
import json
import codecs
import audit_address
import audit_contact

#Files
OSM_FILE = "bh_map.osm"
JSON_NODE_OUT = codecs.open("bh_node.json", "w", "utf-8")
JSON_WAY_OUT = codecs.open("bh_way.json", "w", "utf-8")
JSON_RELATION_OUT = codecs.open("bh_relation.json", "w", "utf-8")

#Attrib to be mapped to the 'created' structure in JSON
CREATED_ATTRIBS = ["version",
                   "changeset",
                   "timestamp",
                   "user",
                   "uid"]

#Others tags to be convert from OSM to JSON file.
#Address and contact are mapped in specif audit files
KEYS_TO_CONVERT = ["amenity",
                   "name",
                   "shop",
                   "leisure",
                   "cuisine",
                   "highway",
                   "landuse",
                   "operator",
                   "area",
                   "sport",
                   "sport_1",
                   "sport_2",
                   "microbrewery",
                   "type"]

def convert_address_tag_element(element, address_node):
    """
    Verify and convert address data from OSM file to JSON structure, using audit_address.py script
    """
    if audit_address.is_street_element(element):
        street_type, street_name = audit_address.process_steet_type_and_name(element.attrib['v'])
        address_node["street_type"] = street_type
        address_node["street"] = street_name
    elif audit_address.is_city_element(element):
        address_node["city"] = audit_address.city_name_cleaning(element.attrib['v'])
    elif audit_address.is_zipcode_element(element):
        zipcode = audit_address.clean_zipcode(element.attrib['v'])
        if zipcode:
            address_node["zipcode"] = zipcode
    elif audit_address.is_address_number_element(element):
        number, housename = audit_address.clean_address_number(element.attrib['v'])
        if number:
            address_node["number"] = number
        if housename:
            address_node["housename"] = housename
    elif audit_address.is_suburb_element(element):
        suburb = audit_address.process_suburb_name(element.attrib['v'])
        if suburb:
            address_node["suburb"] = suburb
    else:
        address_node[element.attrib['k']] = element.attrib['v']
    return address_node

def convert_contact_tag_element(tag_element, contact_node):
    """
    Verify and convert contact data from OSM file to JSON structure, using audit_contact.py script
    """
    if audit_contact.is_phone_element(tag_element):
        phone = audit_contact.process_phone_number(tag_element.attrib['v'])
        if phone:
            if "phone" in contact_node:
                contact_node["phone"].append(phone)
            else:
                contact_node["phone"] = phone
    if audit_contact.is_email_element(tag_element):
        email = audit_contact.check_email(tag_element.attrib['v'])
        if email:
            contact_node["email"] = email
    if audit_contact.is_site_element(tag_element):
        site = audit_contact.check_site(tag_element.attrib['v'])
        if site:
            contact_node["site"] = site
    return contact_node

def convert_way_node_refs(element):
    """
    Convert node refences (nd elements) for 'way' elements
    """
    node_refs = []
    for node_ref in element.iter("nd"):
        node_refs.append(int(node_ref.attrib['ref']))
    return node_refs

def convert_member_element(element):
    """
    Convert members elements from 'relation' elements to JSON format
    """
    member_list = {}
    for member in element.iter("member"):
        if member.attrib['type'] == "way":
            if 'ways' not in member_list:
                member_list['ways'] = []
            member_list['ways'].append(int(member.attrib['ref']))
        if member.attrib['type'] == "node":
            if 'nodes' not in member_list:
                member_list['nodes'] = []
            member_list['nodes'].append(int(member.attrib['ref']))
    return member_list

def get_creation_information(element):
    """ Extract creation information from OSM element """
    created = {}
    for attrib in CREATED_ATTRIBS:
        if attrib in element.attrib:
            created[attrib] = element.attrib[attrib]
    return created

def convert_tag_element(element, node):
    """
    Convert the common tag data structure from OSM to the JSON file
    """
    for tag_element in element.iter("tag"):
        #Convert address data
        if tag_element.attrib['k'] in audit_address.VALID_ADDRESS_TAG:
            if "address" not in node:
                node["address"] = {}
            node["address"] = convert_address_tag_element(tag_element, node["address"])
        #Convert contact data
        if tag_element.attrib['k'] in audit_contact.VALID_CONTACT_TAG:
            if "contact" not in node:
                node["contact"] = {}
            node["contact"] = convert_contact_tag_element(tag_element, node["contact"])
        #Convert other tags
        if tag_element.attrib['k'] in KEYS_TO_CONVERT:
            if (tag_element.attrib['k'].startswith("sport")):
                if "sport" not in node:
                    node["sport"] = [] 
                node["sport"] = convert_sports(tag_element.attrib['v'], node["sport"])
            else:
                node[tag_element.attrib['k']] = tag_element.attrib['v']
    return node

def convert_sports(sport_name, sports_list):
    """
    Convert data in sports tag.
    Sports can be registered as list separated by semicolon or colon
    If there is a sports already record, the new sport is appended to list
    """
    if sport_name.find(";") > -1:
        sport_list_temp = sport_name.split(";")
    elif sport_name.find(",") > -1:
        sport_list_temp = sport_name.split(",")
    else:
        sport_list_temp = [sport_name]

    for sport in sport_list_temp:
        sport = sport.strip()
        if sport not in sports_list:
            sports_list.append(sport)

    return sports_list

def convert_element(element):
    """ Convert OSM element to JSON """
    if element.tag == "node" or element.tag == "way" or element.tag == "relation":
        #Common data convertion
        node = {}
        node['id'] = int(element.attrib['id'])
        node['created'] = get_creation_information(element)

        node['data_type'] = element.tag

        #Get position data for node type elements
        if element.tag == "node":
            node['position'] = [float(element.attrib['lat']), float(element.attrib['lon'])]

        #Convert tag elements
        node = convert_tag_element(element, node)

        #Convert nd elements from a way
        if element.tag == "way":
            node_refs = convert_way_node_refs(element)
            if len(node_refs) > 0:
                node["node_refs"] = node_refs

        elif element.tag == "relation":
            members =  convert_member_element(element)
            if len(members) > 0:
                node['members'] = members

        return node

    else:
        return None

def record_document(elem_type, elem, pretty):
    """
    Check the elemet type to determine which JSON file should be written
    """
    if elem_type == "node":
        out = JSON_NODE_OUT
    elif elem_type == "way":
        out = JSON_WAY_OUT
    elif elem_type == "relation":
        out = JSON_RELATION_OUT

    if pretty:
        out.write(json.dumps(elem, indent=2)+"\n")
    else:
        out.write(json.dumps(elem) + "\n")

def convert_file(file_in, pretty=False):
    """ Convert an OSM file to a JSON format """
    osm_file_in = codecs.open(file_in, 'r', 'utf-8')
    for _, element in ET.iterparse(osm_file_in, events=("start",)):
        elem = convert_element(element)
        if elem:
            record_document(element.tag, elem, pretty)

def main():
    """ Main function """
    convert_file(OSM_FILE, True)

if __name__ == "__main__":
    main()
