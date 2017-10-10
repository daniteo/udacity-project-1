import xml.etree.cElementTree as ET
import re
from collections import defaultdict

OSM_FILE = "bh_map.osm"

street_type_re = re.compile(r'^\S+\.?\b', re.IGNORECASE)
zipcode_re = re.compile(r'[0-9]{5}-{1}[0-9]{3}')
address_number_re = re.compile(r'^[0-9]+')

street_type_list = {}
suburb_list = []
city_list = []

invalid_address_number_list = []
invalid_zipcode_list = []

#Street Audit Structure
valid_street_type = ["Alameda","Avenida","Praça","Rodovia","Rua"]

street_type_mapping_replace = {
    "Av" : "Avenida",
    "Avendia" : "Avenida",
    "Anél" : "Anel",
    "Avenid" : "Avenida",
    "Eua" : "Rua",
    "Alamedas": "Alameda"
}

street_type_mapping_add = {
    "Br" : "Rodovia",
    "Br-381" : "Rodovia",
    "Dos": "Rua",
    "Francisco": "Rua",
    "Paraíba": "Rua",
    "Montes": "Rua",
    "Contorno": "Avenida",
    "Pium-i": "Rua",
    "Riachuelo": "Rua",
    "São" : "Rua"
}

#City Audit Structure
valid_city_name = ["Belo Horizonte", "Contagem"]

city_name_mapping = {
    "bh" : "Belo Horizonte",
    "Belo horizonte" : "Belo Horizonte",
    "Belo Horizonte/MG" : "Belo Horizonte",
    "belo horizonte" : "Belo Horizonte",
    "BELO hORIZONTE" : "Belo Horizonte",
    "Belo Horizonte - MG" : "Belo Horizonte",
    "belo Horizonte" : "Belo Horizonte",
    "Belo Horizonte MG Brazil" : "Belo Horizonte",
    "CONTAGEM" : "Contagem",
    "SANTA LUZIA" : "Santa Luzia",
    "Santa luzia" : "Santa Luzia"
}

def audit_steet_type(street_name):
    match = street_type_re.search(street_name)
    if (match):
        street_type = match.group().lower().capitalize()
        if street_type in street_type_mapping_replace:  
            street_name = street_name.replace(street_type, street_type_mapping_replace[street_type])
            street_type = street_type_mapping_replace[street_type]
        elif street_type in street_type_mapping_add:  
            street_type = street_type_mapping_add[street_type]
            street_name = street_type+" "+street_name
        if street_type not in valid_street_type:
            if street_type not in street_type_list:
                street_type_list[street_type] = []
            street_type_list[street_type].append(street_name)
    return street_type, street_name

def audit_suburb_name(suburb):
    if suburb not in suburb_list:
        suburb_list.append(suburb)

def audit_address_number(number):
    if address_number_re.fullmatch(number) == None:
#        match = address_number_re.search(number)
#        if match:
#            return int (match.group())
        invalid_address_number_list.append(number)
    else:
        return int(number)

def city_name_cleaning(city):
    if city in city_name_mapping:
        city = city_name_mapping[city]
    return city

def audit_city_name(city): 
    city = city_name_cleaning(city)   
    if city not in city_list:
        city_list.append(city)

def audit_zipcode(zipcode):
    match = zipcode_re.match(zipcode)
    if match == None:
        if len(zipcode) == 8:
            return zipcode[:5]+"-"+zipcode[5:]
        elif len(zipcode) == 5:
            return zipcode+"-000"
        elif len(zipcode) == 10 and zipcode[2] == ".":
            return zipcode.replace(".","")
        else:
            invalid_zipcode_list.append(zipcode)
            return ""
    else:
        return zipcode

def is_address_element(element):
    """ Check if the element belongs to a address tag """
    return element.tag == "tag" and element.attrib['k'].startswith("addr")

def is_street_element(element):
    """ Check if the element belongs to a street address tag """
    return element.tag == "tag" and element.attrib['k'] == "addr:street"

def is_suburb_element(element):
    """ Check if the element belongs to a suburb address tag """
    return element.tag == "tag" and element.attrib['k'] == "addr:suburb"

def is_city_element(element):
    return element.tag == "tag" and element.attrib['k'] == "addr:city"

def is_address_number_element(element):
    """ Check if the element belongs to a number address tag """
    return element.tag == "tag" and element.attrib['k'] == "addr:housenumber"

def is_zipcode_element(element):
    """ Check if the element belongs to a zipcode address tag """
    return element.tag == "tag" and (element.attrib['k'] == "postal_code" or element.attrib['k'] == "addr:postcode")

def audit_address(filename):
    """ Check the address data from OSM file """
    for _, element in ET.iterparse(filename, events=("start",)):
        if is_street_element(element):
            audit_steet_type(element.attrib['v'])
        elif is_suburb_element(element):
            audit_suburb_name(element.attrib['v'])
        elif is_address_number_element(element):
            audit_address_number(element.attrib['v'])
        elif is_zipcode_element(element):
            audit_zipcode(element.attrib['v'])
        elif is_city_element(element):
            audit_city_name(element.attrib['v'])

def main():
    """ 
    Main function
    Used to audit address data, checking which verification/changing its necessary to be done.
    """
    audit_address(OSM_FILE)
    print(street_type_list)
    print(invalid_zipcode_list)
    print("\nInvalid address numbers:\n {0}\n".format(invalid_address_number_list))
    print("\nCity list:\n {0}\n".format(city_list))

if __name__ == "__main__":
    main()