# -*- coding: utf-8 -*-
# Copyright (c) 2021, Lin To and Contributors
# See license.txt

import frappe
from copy import deepcopy


def get_doc_names(module):
    temp = frappe.db.get_all("DocType", filters=dict(module=module))
    return [d["name"] for d in temp]


def delete_all_docs(name):
    try:
        records = frappe.db.get_all(name)
        for record in records:
            frappe.db.delete(name, dict(name=record["name"]))
    except frappe.db.TableMissingError:
        pass


def get_autonamed_items(items):
    items = deepcopy(items)
    for item_entry in items:
        item_entry.update({"item": get_item_autoname(item_entry)})
    return items


def check_if_doc_exists(doctype, doc_dict):
    return len(frappe.db.get_all(doctype, filters=doc_dict)) > 0


def get_item_autoname(item_entry):
    record = frappe.db.get_all("Item", filters={"item_name": item_entry["item"]})
    return record[0]["name"]
