# -*- coding: utf-8 -*-
# Copyright (c) 2021, Lin To and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe.model.document import Document


class PaymentEntry(Document):
    def validate(self):
        pass

    def on_submit(self):
        self.add_ledger_entries()

    # def get_ledger_entry(self, account, against_account, credit, debit):

    def get_ledger_entries_for_pay(self):
        credit_entry = self.get_ledger_entry(
            self.account_paid_from,
            self.party_name,
            credit=self.paid_amount,
            debit=0.0,
        )

        debit_entry = self.get_ledger_entry(
            self.account_paid_to,
            self.account_paid_from,
            credit=0.0,
            debit=self.paid_amount,
        )
        return credit_entry, debit_entry

    def get_ledger_entries_for_receive(self):
        credit_entry = self.get_ledger_entry(
            self.account_paid_from,
            self.account_paid_to,
            credit=self.paid_amount,
            debit=0.0,
        )

        debit_entry = self.get_ledger_entry(
            self.account_paid_to,
            self.party_name,
            credit=0.0,
            debit=self.paid_amount,
        )
        return credit_entry, debit_entry

    def add_ledger_entries(self):
        if self.payment_type == "Pay":
            credit_entry, debit_entry = self.get_ledger_entries_for_pay()
        elif self.payment_type == "Receive":
            credit_entry, debit_entry = self.get_ledger_entries_for_receive()
        else:
            frappe.throw(f"Invalid Payment Type :{self.payment_type}")
        # Create Ledger Entries
        self.insert_ledger_entries(credit_entry, debit_entry)

    def insert_ledger_entries(credit_entry, debit_entry):
        # Insert Ledger Entries
        for gl_entry in [credit_entry, debit_entry]:
            gl_entry.docstatus = 1
            gl_entry.insert(ignore_permissions=True, ignore_if_duplicate=True)

    def get_ledger_entry(self, account, against_account, credit, debit):
        return frappe.get_doc(
            doctype="GL Entry",
            posting_date=self.posting_date,
            account=account,
            against_account=against_account,
            credit=credit,
            debit=debit,
            voucher_type=f"Payment Entry",
            company_name=self.company,
            voucher_number=self.name,
        )
