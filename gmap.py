#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This modules allowed to extract data from Google Maps to be used as input to OpenStreetMap.
"""
import requests

URL2 = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=-19.85,-43.9&radius=50000&type=brewery&keyword=cervejarias&key=AIzaSyDBix1OGvPyct_W3tmN_J7p_WpN_vAvuA0"
URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
LOCATION = "-19.85,-43.9"
RADIUS = 50000
TYPE="brewery"
KEYWORD="Cervejarias"
API_KEY = "AIzaSyDBix1OGvPyct_W3tmN_J7p_WpN_vAvuA0"

def show_information(place):
    print("Nome: "+place["name"])
    print("Localização > Lon {0} Lat {1}: ".format(place["geometry"]["location"]["lng"], place["geometry"]["location"]["lat"]))
    print("Endereço: "+place["vicinity"])
    print("")

def get_json(page_token=None):
    """
    Query Google Maps for the data 
    """
    params = {
        "location" : LOCATION,
        "radius" : RADIUS,
        "type" : TYPE,
        "keyword" : KEYWORD,
        "key" : API_KEY
    }

    if page_token:
        params["pagetoken"] = page_token
        print(params)

    r = requests.get(URL, params=params)
    if r.status_code == requests.codes.ok:
        return r.json()
    else:
        return None

def main():
    """
    Main function
    """
    data = get_json()
    for record in data["results"]:
        show_information(record)

    while "next_page_token" in data:
        data = get_json(data["next_page_token"])
        print(data)
        for record in data["results"]:
            show_information(record)


if __name__ == "__main__":
    main()