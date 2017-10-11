"""
Prepare the OSM file from Belo Horizonte to a JSON format to be imported to MongoDB
"""
import xml.etree.cElementTree as ET
import pprint
import time
import json
import codecs
import audit_address
import audit_contact


OSM_FILE = "bh_map.osm"
CREATED_TAGS = ["version", "changeset", "timestamp", "user", "uid"]
KEYS_TO_CONVERT = ["amenity", "name"]
JSON_DATA = []

def prepare_element(element):
    """ Convert OSM element to JSON """
    if element.tag == "node" or element.tag == "way" or element.tag == "relation":
        #Common data convertion
        node = {}
        node['id'] = int(element.attrib['id'])
        node['type'] = element.tag
        node['created'] = get_creation_information(element)
        #Specific data convertion
        if element.tag == "node":
            return prepare_node_element(element, node)
        elif element.tag == "way":
            return prepare_way_element(element, node)
        elif element.tag == "relation":
            return prepare_relation_element(element, node)
    else:
        return None

def convert_address_tag_element(tag_element, address_node):
    """ Convert the address data from OSM file to JSON structure """
    if audit_address.is_street_element(tag_element):
        street_type, street_name = audit_address.process_steet_type_and_name(tag_element.attrib['v'])
        address_node["street_type"] = street_type
        address_node["street"] = street_name
    if audit_address.is_city_element(tag_element):
       address_node["city"] = audit_address.city_name_cleaning(tag_element.attrib['v'])
    if audit_address.is_zipcode_element(tag_element):
        address_node["zipcode"] = audit_address.clean_zipcode(tag_element.attrib['v'])
    if audit_address.is_address_number_element(tag_element):
        pass
    if audit_address.is_suburb_element(tag_element):
        address_node["suburb"] = tag_element.attrib['v']
    return address_node

def convert_contact_tag_element(tag_element, contact_node):
    """ Convert the contact data from OSM file to JSON structure """
    if audit_contact.is_phone_element(tag_element):
        pass
    if audit_contact.is_email_element(tag_element):
        pass
    if audit_contact.is_site_element(tag_element):
        pass
    return contact_node

def prepare_node_element(element, node):
    """ Convert 'node' elements to JSON format """
    node['position'] = [float(element.attrib['lat']), float(element.attrib['lon'])]
    for tag_element in element.iter("tag"):
        #Convert address data
        if tag_element.attrib['k'] in audit_address.valid_address_tag:
            if "address" not in node:
                node["address"] = {}
            node["address"] = convert_address_tag_element(tag_element,node["address"])
        #Convert contact data
        if tag_element.attrib['k'] in audit_contact.valid_contact_tag:
            if "contact" not in node:
                node["contact"] = {}
            node["contact"] = convert_contact_tag_element(tag_element, node["contact"])
        #Convert other tags
        if tag_element.attrib['k'] in KEYS_TO_CONVERT:
            node[tag_element.attrib['k']] = tag_element.attrib['v']

    return node

def prepare_way_element(element, node):
    """ Convert 'way' elements to JSON format """
    for node_ref in element.iter("nd"):
        if 'node_refs' not in node:
            node['node_refs'] = []
        node['node_refs'].append(node_ref.attrib['ref'])
    return node

def prepare_relation_element(element, node):
    """ Convert 'relation' elements to JSON format """
    for member in element.iter("member"):
        if 'members' not in node:
            node['members'] = {}
        if member.attrib['type'] == "way":
            if 'ways' not in node['members']:
                node['members']['ways'] = []
            node['members']['ways'].append(member.attrib['ref'])
        if member.attrib['type'] == "node":
            if 'nodes' not in node['members']:
                node['members']['nodes'] = []
            node['members']['nodes'].append(member.attrib['ref'])
    return node

def get_creation_information(element):
    """ Extract creation information from OSM element """
    created = {}
    for tag in CREATED_TAGS:
        if tag in element.attrib:
            created[tag] = element.attrib[tag]
    return created

def convert_file(file_in, pretty=False):
    """ Convert an OSM file to a JSON format """
    file_out = "{0}_{1}.json".format(file_in, time.time())
    with codecs.open(file_out, "w") as out:
        for _, element in ET.iterparse(file_in, events=("start",)):
            elem = prepare_element(element)
            if elem:
                JSON_DATA.append(elem)
                if pretty:
                    out.write(json.dumps(elem, indent=2)+"\n")
                else:
                    out.write(json.dumps(elem) + "\n")

def main():
    """ Main function """
    convert_file(OSM_FILE, True)
    pprint.pprint(JSON_DATA)

if __name__ == "__main__":
    main()
