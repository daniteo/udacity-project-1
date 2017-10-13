"""
Audit shop and amenties tags
"""
import xml.etree.cElementTree as ET
import codecs

OSM_FILE = "bh_map.osm"

TAGS_KEY = {}

AMENITIES_LIST = set()
INVALID_AMENITIES_LIST = ['Avenida Senhora do Porto', 'General']

SHOP_LIST = set()
INVALID_SHOP_LIST = ['yes']

def process_amenity_key(amenity):
    """ Cleaning amenity key data """
    if amenity not in INVALID_AMENITIES_LIST:
        try:
            return str(amenity.replace("_", " "))
        except UnicodeEncodeError:
            return None
    else:
        return None

def audit_amenity(amenity):
    """ Audit amenity key data """
    amenity = process_amenity_key(amenity)
    if amenity:
        AMENITIES_LIST.add(amenity)

def process_shop_key(shop):
    """ Clening shop key data """
    if shop.find(";") > 0:
        shop = shop.split(";")[0]
    if shop not in INVALID_SHOP_LIST:
        try:
            return str(shop.replace("_", " "))
        except UnicodeEncodeError:
            return None
    else:
        return None

def audit_shop(shop):
    """ Audit shop key data """
    shop = process_amenity_key(shop)
    if shop:
        SHOP_LIST.add(shop)

def is_shop(element):
    """ Check if element belongs to a shop tag """
    return element.tag == "tag" and element.attrib['k'] == "shop"

def is_amenity(element):
    """ Check if element belongs to a amanity tag """
    return element.tag == "tag" and element.attrib['k'] == "amenity"

def audit_contact(filename):
    """ Check the address data from OSM file """
    osmfile = codecs.open(filename, "r", "utf-8")
    for _, element in ET.iterparse(filename, events=("start",)):
        if element.tag == "tag":
            if element.attrib['k'] not in TAGS_KEY:
                TAGS_KEY[element.attrib['k']] = 1
            else:
                TAGS_KEY[element.attrib['k']] += 1
        if is_amenity(element):
            audit_amenity(element.attrib['v'])
        elif is_shop(element):
            audit_shop(element.attrib['v'])


def main():
    """ Main function """
    audit_contact(OSM_FILE)
    print "Amenities: \n{0}\n".format(sorted(AMENITIES_LIST))
    print "Shop: \n{0}\n".format(sorted(SHOP_LIST))
    for key in TAGS_KEY:
        if TAGS_KEY[key] >= 1000:
            print key+" - "+str(TAGS_KEY[key])

if __name__ == "__main__":
    main()
