"""
Audit contact data from nodes and ways
"""
import xml.etree.cElementTree as ET
import re

OSM_FILE = "bh_map.osm"

valid_contact_tag = ["contact:phone", "phone", "contact:email", "email", "contact:website", "website"]

PHONENUMBER_RE = re.compile(r'\+?[5]{0,2} *.?31.? *(9?[0-9]{4}[\- ]?[0-9]{4})$')
PHONENUMBER_ONLYNUMBER_RE = re.compile(r'(9?[0-9]{4}[\- ]?[0-9]{4}$)')
EMAIL_RE = re.compile(r'^\S+@\S+\.\w+\.?\w?')
SITE_RE = re.compile(r'^(https?://|w{3}\.|[A-Za-z0-9]+\.)')

invalid_phone_number_list = []
invalid_email_list = []
invalid_website_list = []

contacts_tags = set()

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
    Remove double spaces and parentesis and
    check if the phone number match the format +55 31 [X]XXXX-XXXX ou +55 31 [X]XXXX XXXX.
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

    return phone

def audit_phone_number(phonenumber):
    """
    Log invalid phone numbers to be evaluated
    """
    phone_list = convert_phone_number_to_list(phonenumber)

    returned_phone_list = []

    for phone in phone_list:
        cleaned_phone = process_phone_number(phone)
        if cleaned_phone:
            returned_phone_list.append(cleaned_phone)
        else:
            invalid_phone_number_list.append(phone)

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
    email = check_email(email)
    if not email:
       invalid_email_list.append(email)

def audit_website(site):
    if not SITE_RE.search(site):
        invalid_website_list.append(site)

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
        if has_contact_attr(element):
            contacts_tags.add(element.attrib['k'])
        if is_phone_element(element):
            audit_phone_number(element.attrib['v'])
        elif is_email_element(element):
            audit_email(element.attrib['v'])
        elif is_site_element(element):
            audit_website(element.attrib['v'])

def main():
    """ Main function """
    audit_contact(OSM_FILE)
    print("Estrutura: \n{0}\n".format(sorted(contacts_tags)))
    print("Telefones com formatos inválidos: \n{0}\n".format(invalid_phone_number_list))
    print("Emails inválidos: \n{0}\n".format(invalid_email_list))
    print("Sites inválidos: \n{0}\n".format(invalid_website_list))

if __name__ == "__main__":
    main()