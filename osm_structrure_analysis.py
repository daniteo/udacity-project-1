import xml.etree.cElementTree as ET
import pprint

OSM_FILE = "bh_map.osm"
DATA_STRUCTURE = {
    'node': {
        'attribs': [],
        'tags': [],
        'properties': []
    },
    'way': {
        'attribs': [],
        'tags': [],
        'properties': []
    },
    'relation': {
        'attribs': [],
        'tags': [],
        'properties': []
    }
}

def check_file_structure(filename):
    """ Check the OSM file structure before convert to JSON """
    for _, element in ET.iterparse(filename, events=("start",)):
        if element.tag == "node" or element.tag == "way" or element.tag == "relation":
            for attribute in element.attrib:
                if attribute not in DATA_STRUCTURE[element.tag]['attribs']:
                    DATA_STRUCTURE[element.tag]['attribs'].append(attribute)
            for sub_elem in element.iter():
                if sub_elem.tag not in DATA_STRUCTURE[element.tag]['tags']:
                    DATA_STRUCTURE[element.tag]['tags'].append(sub_elem.tag)
                if sub_elem.tag == "tag":
                    if sub_elem.attrib['k'] not in DATA_STRUCTURE[element.tag]['properties']:
                        DATA_STRUCTURE[element.tag]['properties'].append(sub_elem.attrib['k'])


def main():
    check_file_structure(OSM_FILE)
    pprint.pprint(DATA_STRUCTURE)

if __name__ == "__main__":
    main()