#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrai os dados de cervejarias artesanais de Belo Horizonte de um arquivo KML 
para um XML que poderá ser usado para importação no OpenStreetMap.
O resultado deste script é um arquivo XML para importação 
"""
import xml.etree.ElementTree as ET
import requests
import audit_address as addr
import pprint

KML_FILE = "Cervejarias MG.kml"

ns = {'kml':'http://www.opengis.net/kml/2.2'}

URL2 = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=-19.85,-43.9&radius=50000&type=brewery&keyword=cervejarias&key="
URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
LOCATION = "-19.85,-43.9"
RADIUS = 50000

nodes_list = []

def get_maps_api_key():
    """
    Recupera a API KEY do Google Maps a partir do arquivo API_KEY_GMAPS, no mesmo diretório do script.

    Returns:
        string: API KEY presente no arquivo API_KEY_MAPS.
    """
    try:
        with open ('API_KEY_GMAPS', 'r') as file:
            apikey = file.read()
        return apikey 
    except FileNotFoundError:
        print("\nNão foi possível encontrar o arquivo 'API_KEY_GMPAS'.")
        print("Crie este arquivo contendo a API KEY do Google Maps para pesquisa das coordenadas.\n")
        exit()

def get_coordenate(name, address):
    """
    Realiza a pesquisa no Google Maps com o nome e endereço das cervejarias.

    Args:
        name (string): Nome da cervejaria.
        address (string): Endereço da cervejaria.

    Returns:
        dictionary: Coordenadas encontradas no Google Maps para os dados informados
    """
    print(name+" - "+address)
    apikey = get_maps_api_key()

    params = {
        "location" : LOCATION,
        "radius" : RADIUS,
        "keyword" : name+" "+address,
        "key" : apikey
    }

    r = requests.get(URL, params=params)
    if r.status_code == requests.codes.ok:
        data = r.json()
        if "results" in data:
            if len(data["results"]) > 0:
                coordenate = data["results"][0]["geometry"]["location"]
                return coordenate
        return None
    else:
        return None

def process_address(address):
    """
    Separa o endereço completo presente na estrutura KML numa estrutura com 
    endereço, numero, bairro e cidade.

    Args:
        address (string): Endereço completo
    """
    print(address)
    address_data = {}
    address = address.replace("–","-")
    address_array = address.split("-")

    street = address_array[0].strip()
    if street.find(",") > 0:
        street_data = street.split(",")
        address_data["street"] = street_data[0]
        address_data["housenumber"] = street_data[1]
    else:
        address_data["street"] = street

    if len(address_array) > 1:
        suburb = address_array[1].strip().title()
        if suburb in addr.CITY_NAME_IN_BELOHORIZONTE_AREA:
            address_data["city"] = suburb 
        else:
            address_data["suburb"] = suburb 
    if len(address_array) > 2:
        address_data["city"] = address_array[2].strip().title()

    return address_data

def generate_osm_xml():
    """
    Gera o arquivo XML para o OpenStreetMap a partir dos dados extraidos do arquivo KML
    """
    root = ET.Element("osm")
    for node in nodes_list:
        node_xml = ET.SubElement(root, "node", lat=str(node["position"][0]), lon=str(node["position"][1]))

        ET.SubElement(node_xml, "tag", k="name", v=node["name"])
        ET.SubElement(node_xml, "tag", k="addr:street_name", v=node["address"]["street"])
        if "housenumber" in node["address"]:
            ET.SubElement(node_xml, "tag", k="addr:housenumber", v=node["address"]["housenumber"])
        if "suburb" in node["address"]:
            ET.SubElement(node_xml, "tag", k="addr:suburb", v=node["address"]["suburb"])
        if "city" in node["address"]:
            ET.SubElement(node_xml, "tag", k="addr:city", v=node["address"]["city"])
        ET.SubElement(node_xml, "tag", k="microbrewery", v="yes")


    tree = ET.ElementTree(root)
    tree.write("cervejaria.xml",encoding="UTF-8",xml_declaration=True)
    
def convert_file(file_in):
    """
    Realiza a leitura do arquivo KML, preparando os dados para geração do XML com os dados do OSM.
    """
    file_tree = ET.parse(file_in)
    root = file_tree.getroot()

    for document in root.findall('kml:Document', ns):
        for folder in document.findall('kml:Folder', ns):
            for place in folder.findall('kml:Placemark', ns):
                name = place.find('kml:name', ns)
                address = place.find('kml:address', ns)
                address_data = process_address(address.text)
                position = get_coordenate(name.text, address.text)
                if position:
                    node = {
                        "name" : name.text,
                        "address" : address_data,
                        "position" : [position["lat"],position["lng"]]
                    }
                    nodes_list.append(node)
    
    generate_osm_xml()


def main():
    """ Main function """
    convert_file(KML_FILE)

if __name__ == "__main__":
    main()
