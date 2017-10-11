import xml.etree.cElementTree as ET
import re
from collections import defaultdict

OSM_FILE = "bh_map.osm"

valid_contact_tag = ["contact:phone","phone","contact:email","email","contact:website","website"]

phonenumber_re = re.compile(r'\+?55 31 [0-9]{4,5}.[0-9]{4}')
phonenumber_onlynumber_re = re.compile(r'[0-9]{8}$')
email_re = re.compile(r'^\S+@\S+\.\w+\.?\w?')
site_re = re.compile(r'w{3}')

invalid_phone_number_list = []
invalid_email_list = []

def convert_phone_number_to_list(phonenumber):
    """ 
    If there is a number list separeted by semicolon, return an array with the number in list
    """
    if phonenumber.find(";") > 0:
        return phonenumber.split(";")
    else:
        return [phonenumber]

def clean_phone_number(phonenumber):
    """
    Remove double spaces and parentesis and
    check if the phone number match the format +55 31 [X]XXXX-XXXX ou +55 31 [X]XXXX XXXX.
    """
    phonenumber = phonenumber.strip()
    phonenumber = phonenumber.replace("  "," ")
    phonenumber = phonenumber.replace("(","")
    phonenumber = phonenumber.replace(")","")

    if phonenumber_onlynumber_re.search(phonenumber):
        phonenumber = "+55 31 "+phonenumber[-8:-4]+"-"+phonenumber[-4:]

    if phonenumber_re.fullmatch(phonenumber):
        if not phonenumber.startswith("+"):
            phonenumber = "+"+phonenumber
        return phonenumber
    else:
        return None

def audit_phone_number(phonenumber):
    """
    Log invalid phone numbers to be evaluated
    """
    phone_list = convert_phone_number_to_list(phonenumber)

    returned_phone_list = []

    for phone in phone_list:
        cleaned_phone = clean_phone_number(phone)
        if (cleaned_phone):
            returned_phone_list.append(cleaned_phone)
        else:
            invalid_phone_number_list.append(phone)

    return returned_phone_list


def audit_email(email):
    """
    Check if the email match the following format:
    - Start with a letter
    - Contain @
    - Contain at least one . 
    """
    match = email_re.search(email)
    if match == None:
       invalid_email_list.append(email)

def audit_website(site):
    if not site_re.search(site):
        print(site)

def is_phone_element(element):
    return element.tag == "tag" and (element.attrib['k'] == "contact:phone" or element.attrib['k'] == "phone")

def is_email_element(element):
    return element.tag == "tag" and (element.attrib['k'] == "contact:email" or element.attrib['k'] == "email")

def is_site_element(element):
    return element.tag == "tag" and (element.attrib['k'] == "contact:website" or element.attrib['k'] == "website")

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
    audit_contact(OSM_FILE)
    print("Telefones com formatos inválidos: \n{0}\n".format(invalid_phone_number_list))
    print("Emails inválidos: \n{0}\n".format(invalid_email_list))

if __name__ == "__main__":
    main()