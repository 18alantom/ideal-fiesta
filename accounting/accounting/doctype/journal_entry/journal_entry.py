# -*- coding: utf-8 -*-
# Copyright (c) 2021, Lin To and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class JournalEntry(Document):

    def validate_accounting_entry_count(self):
        entry_count = len(self.accounting_entries)
        if  entry_count != 2:
            frappe.throw("There should be 2 accounting entries, \n"
                    "This is double entry accounting, "
                    f"not {entry_count} entry accounting.")

    def validate_credit_debit_values(self):
        for entry in self.accounting_entries:
            is_valid = ( entry.credit_in_account == 0 and entry.debit_in_account > 0 ) or \
                       ( entry.credit_in_account > 0 and entry.debit_in_account == 0 )
            if not is_valid:
                frappe.throw("Either credit or debit of an entry should be 0.")

    def validate_credit_debit_difference(self):
        credit = 0
        debit = 0
        for entry in self.accounting_entries:
            credit += entry.credit_in_account
            debit += entry.debit_in_account

        diff = credit - debit
        if abs(diff) > 0:
            frappe.throw("Credit, Debit difference should be 0.")

    def validate_accounting_entries(self):
        self.validate_accounting_entry_count()
        self.validate_credit_debit_values()
        self.validate_credit_debit_difference()

    def get_credit_or_debit_entry(self, account_type):
        for entry in self.accounting_entries:
            if getattr(entry, account_type) > 0:
                return entry

    def get_credit_entry(self): return self.get_credit_or_debit_entry("credit_in_account")
    def get_debit_entry(self): return self.get_credit_or_debit_entry("debit_in_account")

    def get_ledger_entry(self, account, against_account, credit, debit):
        return frappe.get_doc(
            doctype="Ledger Entry",
            posting_date=self.posting_date,
            account=account,
            against_account=against_account,
            credit=credit,
            debit=debit,
            voucher_type="Journal Entry"
        )

    def add_ledger_entries(self):
        # Journal Entries
        credit = self.get_credit_entry()
        debit = self.get_debit_entry()

        # Ledger Entries
        credit_entry = self.get_ledger_entry(credit.account, debit.account, \
                credit.credit_in_account, debit.debit_in_account)
        debit_entry = self.get_ledger_entry(debit.account, credit.account, \
                debit.debit_in_account, credit.credit_in_account)

        # Save Entries
        credit_entry.insert(ignore_permissions=True)
        debit_entry.insert(ignore_permissions=True)

    def validate(self):
        self.validate_accounting_entries()

    def on_submit(self):
        super().on_submit()
        self.add_ledger_entries() # General Ledger Entry
