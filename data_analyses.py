import xml.etree.cElementTree as ET
import re
from collections import defaultdict

OSM_FILE = "bh_map.osm"
street_type_re = re.compile(r'^\S+\.?\b', re.IGNORECASE)
street_type_list = []

street_type_mapping = {
    "Av" : "Avenida",
    "Avendia" : "Avenida",
    "Anél" : "Anel"
}

def audit_steet_type(street_name):
    match = street_type_re.search(street_name)
    if (match):
        street_type = match.group().lower().capitalize()
        if street_type not in street_type_list:
            street_type_list.append(street_type)

def is_street_element(element):
    return element.tag == "tag" and element.attrib['k'] == "addr:street"

def street_name_analiyses(filename):
    """ Check the OSM file structure before convert to JSON """
    for _, element in ET.iterparse(filename, events=("start",)):
        if is_street_element(element):
            audit_steet_type(element.attrib['v'])     

def main():
    street_name_analiyses(OSM_FILE)
    print(street_type_list)

if __name__ == "__main__":
    main()