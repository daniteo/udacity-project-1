"""
Audit addrees contact from OSM file
"""
import xml.etree.cElementTree as ET
import re

OSM_FILE = "bh_map.osm"

#Address tags to be convert from OSM file
VALID_ADDRESS_TAG = ["addr:street",
                     "addr:city",
                     "addr:postcode",
                     "postal_code",
                     "addr:housenumber",
                     "addr:housename",
                     "addr:suburb"]

#Regex used to validate address data
STREET_TYPE_RE = re.compile(r'^[A-ZÀ-Ú]+((\.?\b)|\.)', re.IGNORECASE)
ZIPCODE_RE = re.compile(r'^3[0-9]{4}\-[0-9]{3}')
ADDRESS_NUMBER_RE = re.compile(r'^[0-9]+')
ADDRESS_NUMBER_WITH_NAME_RE = re.compile(r'^([0-9]+) ?[, \-/]? ?([A-Z0-9 º]+)', re.IGNORECASE)

#Data structure used to audit OSM data
SUBURB_NAME_LIST = []
CITY_NAME_LIST = []
INVALID_STREET_TYPE_LIST = {}
INVALID_ADDRESS_NUMBER_LIST = []
INVALID_ZIPCODE_LIST = []

#Street Audit Structure
#Street type expected in structure
VALID_STREET_TYPE = ["Alameda", "Avenida", "Praça", "Rodovia", "Rua", "Anel", "Estrada"]

#Street type that should be replaced from OSM to JSON file
#in order to keep consistency between data. This mapping 
#deal with names typed wrong or abbreviations
STREET_TYPE_MAPPING_REPLACE = {
    "Av" : "Avenida",
    "Avendia" : "Avenida",
    "Anél" : "Anel",
    "Avenid" : "Avenida",
    "Eua" : "Rua",
    "Alamedas": "Alameda"
}

#Street type that should be added to the street name from OSM to JSON file
#Those street name were analyzed in an iterative waym so I can check the 
#street names to identified their types since its wasn't inserted at the name.
STREET_TYPE_MAPPING_ADD = {
    "Br" : "Rodovia",
    "Br-381" : "Rodovia",
    "Dos": "Rua",
    "Francisco": "Rua",
    "Paraíba": "Rua",
    "Montes": "Rua",
    "Contorno": "Avenida",
    "Pium": "Rua",
    "Riachuelo": "Rua",
    "São" : "Rua"
}

#City Audit Structure:
#City names expected in Belo Horizonte area, aka "Grande Belo Horizonte"
CITY_NAME_IN_BELOHORIZONTE_AREA = ["Belo Horizonte",
                                   "Contagem",
                                   "Nova Lima",
                                   "Ribeirão Das Neves",
                                   "Santa Luzia",
                                   "Sabará",
                                   "Ibirité",
                                   "Betim"]

#City name that should be replaced from OSM to JSON file
#in order to keep consistency between data. This mapping 
#deal with names typed wrong or abbreviations
CITY_NAME_MAPPING = {
    "Bh" : "Belo Horizonte",
    "Belo Horizonte/Mg" : "Belo Horizonte",
    "Belo Horizonte - Mg" : "Belo Horizonte",
    "Belo Horizonte Mg Brazil" : "Belo Horizonte"
}

#Suburb name that should be replaced from OSM to JSON file
#in order to keep consistency between data. This mapping 
#deal with names typed wrong 
SUBURB_NAME_MAPPING = {
    "Goiania" : "Goiânia",
    "Padre Eustaquio" : "Padre Eustáquio"
}

def process_steet_type_and_name(street_name):
    """
    Extract street type from street name and verify data,
    correcting wrong data
    """
    street_name = street_name.title()
    street_type = ""
    match = STREET_TYPE_RE.search(street_name)
    if match:
        street_type = match.group()
        if street_type in STREET_TYPE_MAPPING_REPLACE:
            street_name = street_name.replace(street_type, STREET_TYPE_MAPPING_REPLACE[street_type])
            street_type = STREET_TYPE_MAPPING_REPLACE[street_type]
        elif street_type in STREET_TYPE_MAPPING_ADD:
            street_type = STREET_TYPE_MAPPING_ADD[street_type]
            street_name = street_type+" "+street_name
    return street_type, street_name

def audit_steet_type_and_name(street_name):
    """
    Audit street type and name, checking for consitency and incorrect data
    """
    street_type, street_name = process_steet_type_and_name(street_name)
    if street_type not in VALID_STREET_TYPE:
        if street_type not in INVALID_STREET_TYPE_LIST:
            INVALID_STREET_TYPE_LIST[street_type] = []
        INVALID_STREET_TYPE_LIST[street_type].append(street_name)

def process_suburb_name(suburb):
    """
    Check and cleaning suburb name by formating ans mapping name typed
    in differnt ways to keep data consistency
    """
    if suburb in SUBURB_NAME_MAPPING:
        suburb = SUBURB_NAME_MAPPING[suburb]
        suburb = suburb.title()
        #Exclude suburb names record with city names
        if suburb in CITY_NAME_IN_BELOHORIZONTE_AREA:
            return None
        else:
            return suburb

def audit_suburb_name(suburb):
    """
    Audit suburb name, logging in SUBURB_NAME_LIST strutcture after cleaning
    """
    suburb = process_suburb_name(suburb)
    if suburb:
        if suburb.title() not in SUBURB_NAME_LIST:
            SUBURB_NAME_LIST.append(suburb.title())

#Address number audit
def clean_address_number(number):
    """
    Check if the address number, has also a housename appended on it.
    If so, clean the data, separate the housename from the number and
    return both, in separeted vars
    """
    if ADDRESS_NUMBER_RE.fullmatch(number):
        return int(number), None
    else:
        match = ADDRESS_NUMBER_WITH_NAME_RE.fullmatch(number)
        if match:
            number = int(match.group(1))
            housename = match.group(2)
            return number, housename
        else:
            return None, None

def audit_address_number(number):
    """
    Audit address number format
    """
    addr_number, _ = clean_address_number(number)
    if not addr_number:
        INVALID_ADDRESS_NUMBER_LIST.append(number)

def city_name_cleaning(city):
    """
    Check and cleaning suburb name by formating ans mapping name typed
    in differnt ways to keep data consistency
    """
    #Format city name captilizing each word from the name
    city = city.title()
    #Mapping city name
    if city in CITY_NAME_MAPPING:
        city = CITY_NAME_MAPPING[city]
    if city in CITY_NAME_IN_BELOHORIZONTE_AREA:
        return city
    else:
        return None

def audit_city_name(city):
    """
    Audit name city, logging in CITY_NAME_LIST strutcture after cleaning
    """
    city = city_name_cleaning(city)
    if city and city not in CITY_NAME_LIST:
        CITY_NAME_LIST.append(city)

def clean_zipcode(zipcode):
    """
    Clean zipcode value to match the "XXXXX-XXX" format.
     - ZIP Codes with only 5 digits are appended "-000" at the end
     - ZIP Codes registered with digits only have the "-" character inserted
     - Remove "." characters from ZIP Codes
    """
    match = ZIPCODE_RE.search(zipcode)
    if match:
        return match.group(0)
    else:
        if len(zipcode) == 8:
            return zipcode[:5]+"-"+zipcode[5:]
        elif len(zipcode) == 5:
            return zipcode+"-000"
        elif len(zipcode) == 10 and zipcode[2] == ".":
            return zipcode.replace(".", "")
        else:
            return None

def audit_zipcode(zipcode):
    zipcode_cleaned = clean_zipcode(zipcode)
    if not zipcode_cleaned:
        INVALID_ZIPCODE_LIST.append(zipcode)

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
            audit_steet_type_and_name(element.attrib['v'])
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
    print("\nSuburb names:\n {0}\n".format(sorted(SUBURB_NAME_LIST)))
    print("\nCity names:\n {0}\n".format(CITY_NAME_LIST))
    print("\nInvalid street types:\n {0}\n".format(INVALID_STREET_TYPE_LIST))
    print("\nInvalid zipcodes:\n {0}\n".format(INVALID_ZIPCODE_LIST))
    print("\nInvalid address numbers:\n {0}\n".format(INVALID_ADDRESS_NUMBER_LIST))

if __name__ == "__main__":
    main()