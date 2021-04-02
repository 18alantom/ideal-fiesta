# -*- coding: utf-8 -*-
# Copyright (c) 2021, Lin To and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe.model.document import Document

create_default_accounts = frappe.get_module(
    "accounting.accounting.doctype.account.create_default_accounts"
).create_default_accounts


class Company(Document):
    def after_insert(self):
        create_default_accounts(self.company_name)
