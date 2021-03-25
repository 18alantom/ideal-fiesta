# -*- coding: utf-8 -*-
# Copyright (c) 2021, Lin To and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class JournalEntry(Document):

    def validate_accounting_item_count(self):
        item_count = len(self.journal_items)
        if  item_count != 2:
            frappe.throw("There should be 2 accounting entries, \n"
                    "This is double entry accounting, "
                    f"not {item_count} entry accounting.")

    def validate_credit_debit_values(self):
        for item in self.journal_items:
            is_valid = ( item.credit_in_account == 0 and item.debit_in_account > 0 ) or \
                       ( item.credit_in_account > 0 and item.debit_in_account == 0 )
            if not is_valid:
                frappe.throw("Either credit or debit of an entry should be 0.")

    def validate_credit_debit_difference(self):
        credit = 0
        debit = 0
        for item in self.journal_items:
            credit += item.credit_in_account
            debit += item.debit_in_account

        diff = credit - debit
        if abs(diff) > 0:
            frappe.throw("Credit, Debit difference should be 0.")

    def validate_journal_items(self):
        self.validate_accounting_item_count()
        self.validate_credit_debit_values()
        self.validate_credit_debit_difference()

    def get_credit_or_debit_item(self, account_type):
        for item in self.journal_items:
            if getattr(item, account_type) > 0:
                return item

    def get_credit_item(self): return self.get_credit_or_debit_item("credit_in_account")
    def get_debit_item(self): return self.get_credit_or_debit_item("debit_in_account")

    def get_ledger_item(self, account, against_account, credit, debit):
        return frappe.get_doc(
            doctype="GL Entry",
            posting_date=self.posting_date,
            account=account,
            against_account=against_account,
            credit=credit,
            debit=debit,
            voucher_type="Journal Entry"
        )

    def add_ledger_entries(self):
        # Journal Entries
        credit = self.get_credit_item()
        debit = self.get_debit_item()

        # Ledger Entries
        credit_item = self.get_ledger_item(credit.account, debit.account, \
                credit.credit_in_account, debit.debit_in_account)
        debit_item = self.get_ledger_item(debit.account, credit.account, \
                debit.debit_in_account, credit.credit_in_account)

        # Save Entries
        credit_item.insert(ignore_permissions=True)
        debit_item.insert(ignore_permissions=True)

    def validate(self):
        self.validate_journal_items()

    def on_submit(self):
        self.add_ledger_entries() # General Ledger Entry
