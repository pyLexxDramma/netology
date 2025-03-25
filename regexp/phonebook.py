import csv
import re
from pprint import pprint

with open("phonebook_raw.csv", encoding="utf-8") as f:
    rows = csv.reader(f, delimiter=",")
    contacts_list = list(rows)

def format_name(contacts):
    for contact in contacts:
        name_parts = contact[:3]
        formatted_name = " ".join(name_parts).split(" ")
        contact[0] = formatted_name[0]
        contact[1] = formatted_name[1] if len(formatted_name) > 1 else ''
        contact[2] = formatted_name[2] if len(formatted_name) > 2 else ''

def format_phone(contacts):
    phone_pattern = re.compile(r"(\+7|8)?[\s(]*(\d{3})[\s)]*(\d{3})[\s-]*(\d{2})[\s-]*(\d{2})(\s*доб\.(\d+))?")
    for contact in contacts:
        if len(contact) > 5:
            phone = contact[5]
            match = phone_pattern.search(phone)
            if match:
                formatted_phone = f"+7({match.group(2)}){match.group(3)}-{match.group(4)}-{match.group(5)}"
                if match.group(7):
                    formatted_phone += f" доб.{match.group(7)}"
                contact[5] = formatted_phone

def merge_duplicates(contacts):
    unique_contacts = {}
    for contact in contacts:
        key = (contact[0], contact[1])
        if key not in unique_contacts:
            unique_contacts[key] = contact
        else:
            existing_contact = unique_contacts[key]
            for i in range(len(existing_contact)):
                if existing_contact[i] == "" and contact[i] != "":
                    existing_contact[i] = contact[i]
    return list(unique_contacts.values())

format_name(contacts_list)
format_phone(contacts_list)
contacts_list = merge_duplicates(contacts_list)

with open("phonebook.csv", "w", encoding="utf-8", newline='') as f:
    datawriter = csv.writer(f, delimiter=',')
    datawriter.writerows(contacts_list)

pprint(contacts_list)
