# -*- coding: utf-8 -*-
# Copyright (c) 2021, Lin To and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.nestedset import NestedSet

class Account(NestedSet):
    def before_save(self):
        self.currency = frappe.get_doc("Company",self.company).currency

        # Apply name
        acr = ''.join([c for c in self.company if c.isupper()])
        self.name = self.account_name + " - " + acr
