#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract microbrewery data from KML file to populate OSM database
"""
import xml.etree.ElementTree as ET
import requests

KML_FILE = "Cinturão da cevada - Minas Gerais.kml"

ns = {'kml':'http://www.opengis.net/kml/2.2'}

URL2 = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=-19.85,-43.9&radius=50000&type=brewery&keyword=cervejarias&key="
URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
LOCATION = "-19.85,-43.9"
RADIUS = 50000

def get_maps_api_key():
    with open ('API_KEY_GMAPS', 'r') as file:
        apikey = file.read()
    return apikey 

def get_coordenate(endereco):
    """
    Query Google Maps for the data 
    """
    params = {
        "location" : LOCATION,
        "radius" : RADIUS,
        "keyword" : endereco,
        "key" : get_maps_api_key()
    }

    r = requests.get(URL, params=params)
    if r.status_code == requests.codes.ok:
        data = r.json()
        coordenate = data["results"][0]["geometry"]["location"]
        return coordenate
    else:
        return None
    

def convert_file(file_in):
    file_tree = ET.parse(file_in)
    root = file_tree.getroot()

    for document in root.findall('kml:Document', ns):
        for folder in document.findall('kml:Folder', ns):
            for place in folder.findall('kml:Placemark', ns):
                name = place.find('kml:name', ns)
                address = place.find('kml:address', ns)
                position = get_coordenate(address.text)
                osm_node = {
                    "name" : name.text,
                    "position" : [position["lat"],position["lng"]]
                }
                print(osm_node)


def main():
    """ Main function """
    convert_file(KML_FILE)

if __name__ == "__main__":
    main()
