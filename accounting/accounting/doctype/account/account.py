# -*- coding: utf-8 -*-
# Copyright (c) 2021, Lin To and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.nestedset import NestedSet

def get_account_name(account_name, company_name):
    acronym = ''.join([c for c in company_name if c.isupper()])
    return account_name + " - " + acronym
    

class Account(NestedSet):
    def before_save(self):
        self.currency = frappe.get_doc("Company",self.company).currency

        # Apply name
        self.name = get_account_name(self.account_name, self.company)
