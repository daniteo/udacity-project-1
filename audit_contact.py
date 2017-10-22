#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Audit contact data from nodes and ways
"""
import xml.etree.cElementTree as ET
import re

OSM_FILE = "bh_map.osm"

#Contact tags to be converted from OSM file
VALID_CONTACT_TAG = ["contact:phone",
                     "phone",
                     "contact:email",
                     "email",
                     "contact:website",
                     "website"]

#Regular expressions used to validate contact data
PHONENUMBER_RE = re.compile(r'\+?[5]{0,2} *.?31.? *(9?[0-9]{4}[\- ]?[0-9]{4})$')
PHONENUMBER_ONLYNUMBER_RE = re.compile(r'(9?[0-9]{4}[\- ]?[0-9]{4}$)')
EMAIL_RE = re.compile(r'^\S+@\S+\.\w+\.?\w?')
SITE_RE = re.compile(r'^(https?://|w{3}\.|[A-Za-z0-9]+\.)')

#Structructure used for audit, storing invalid data in OSM fila
INVALID_PHONE_NUMBER_LIST = []
INVALID_EMAIL_LIST = []
INVALID_WEBSITE_LIST = []

def convert_phone_number_to_list(phonenumber):
    """
    If there is a number list separeted by semicolon, return an array with the number in list
    """
    if phonenumber.find(";") > 0:
        return phonenumber.split(";")
    else:
        return [phonenumber]

def process_phone_number(phonenumber):
    """
    Verify telephone numbers by matching it with the phones regex pattern
    and normalize it to format +55 31 9xxxx-xxxx
    """

    match = PHONENUMBER_RE.fullmatch(phonenumber.strip())

    phone = None
    if match:
        phone = match.group(1)
    else:
        match = PHONENUMBER_ONLYNUMBER_RE.fullmatch(phonenumber.strip())
        if match:
            phone = match.group(1)

    if phone:
        #Replace whitespace separator for hifen (-)
        phone = phone.replace(" ", "-")
        #If phone has only nubers
        if phone.find("-") == -1:
            phone = phone[:-4]+"-"+phone[-4:]

    if phone:
        phone = "+55 31 "+phone

    return phone

def audit_phone_number(phonenumber):
    """
    Log phone numbers the not match the pattern to array invalid_phone_number_list
    """
    phone_list = convert_phone_number_to_list(phonenumber)

    returned_phone_list = []

    for phone in phone_list:
        cleaned_phone = process_phone_number(phone)
        if cleaned_phone:
            returned_phone_list.append(cleaned_phone)
        else:
            INVALID_PHONE_NUMBER_LIST.append(phone)

    return returned_phone_list


def check_email(email):
    """
    Check if the email match the following format:
    - Start with a letter
    - Contain @
    - Contain at least one .
    """
    match = EMAIL_RE.search(email)
    if match:
        return email
    else:
        return None

def audit_email(email):
    """
    Log invalid email (not match email pattern) to array INVALID_EMAIL_LIST
    """
    if not check_email(email):
        INVALID_EMAIL_LIST.append(email)

def check_site(site):
    """
    Check if the site match the the webite pattern:
    """
    if SITE_RE.search(site):
        return site
    else:
        return None

def audit_website(site):
    """
    Log invalid site (not match site pattern) to array INVALID_WEBSITE_LIST
    """
    if not check_site(site):
        INVALID_WEBSITE_LIST.append(site)

def is_phone_element(element):
    """ Check if element belongs to a phone number data """
    return element.tag == "tag" and (element.attrib['k'] == "contact:phone_1" or element.attrib['k'] == "contact:phone" or element.attrib['k'] == "phone")

def is_email_element(element):
    """ Check if element belongs to a email data """
    return element.tag == "tag" and (element.attrib['k'] == "contact:email" or element.attrib['k'] == "email")

def is_site_element(element):
    """ Check if element belongs to a website data """
    return element.tag == "tag" and (element.attrib['k'] == "contact:website" or element.attrib['k'] == "website")

def has_contact_attr(element):
    """ Check if element belongs to a contact data """
    return element.tag == "tag" and (element.attrib['k'].startswith("contact:") or element.attrib['k'].find("site") >= 0 or element.attrib['k'].find("mail") >= 0)

def audit_contact(filename):
    """ Check the address data from OSM file """
    for _, element in ET.iterparse(filename, events=("start",)):
        if is_phone_element(element):
            audit_phone_number(element.attrib['v'])
        elif is_email_element(element):
            audit_email(element.attrib['v'])
        elif is_site_element(element):
            audit_website(element.attrib['v'])

def main():
    """ Main function """
    audit_contact(OSM_FILE)
    print("Telefones com formatos inválidos: \n{0}\n".format(INVALID_PHONE_NUMBER_LIST))
    print("Emails inválidos: \n{0}\n".format(INVALID_EMAIL_LIST))
    print("Sites inválidos: \n{0}\n".format(INVALID_WEBSITE_LIST))

if __name__ == "__main__":
    main()
