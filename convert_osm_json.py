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

def prepare_node_element(element, node):
    """ Convert 'node' elements to JSON format """
    node['position'] = [float(element.attrib['lat']), float(element.attrib['lon'])]
    for tag_element in element.iter("tag"):
        if audit_address.is_street_element(tag_element):
            if "address" not in node:
                node["adsress"]
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
    convert_file(OSM_FILE)
    #pprint.pprint(JSON_DATA)

if __name__ == "__main__":
    main()
