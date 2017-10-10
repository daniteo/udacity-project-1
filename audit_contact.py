import xml.etree.cElementTree as ET
import re
from collections import defaultdict

OSM_FILE = "bh_map.osm"

phonenumber_re = re.compile(r'\+55 31 [0-9]{4}.?[0-9]{4}')
email_re = re.compile(r'^\S+@\S+\.\w+\.?\w?')
site_re = re.compile(r'w{3}')

invalid_phone_number_list = []
invalid_email_list = []

def audit_phone_number(phonenumber):
    """ 
    Remove double spaces and parentesis and
    check if the phone number match the format +55 31 XXXX-XXXX ou +55 31 XXXXXXXX.
    If there is a number list separeted by semicolon, return an array with the number in list
    """
    phonenumber = phonenumber.replace("  "," ")
    phonenumber = phonenumber.replace("("," ")
    phonenumber = phonenumber.replace(")"," ")

    if phonenumber_re.fullmatch(phonenumber):
        return [phonenumber]
    elif phonenumber.find(";") > 0:
         phone_list = phonenumber.split(";")
         for phone in phone_list:
            if phonenumber_re.fullmatch(phone) == None:
                invalid_email_list.append(phonenumber)
            else:
                return phone_list
    else:
        invalid_phone_number_list.append(phonenumber)

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
    return element.tag == "tag" and element.attrib['k'] == "contact:phone"

def is_email_element(element):
    return element.tag == "tag" and element.attrib['k'] == "contact:email"

def is_site_element(element):
    return element.tag == "tag" and element.attrib['k'] == "contact:website"

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