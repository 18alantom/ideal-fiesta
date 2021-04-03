# -*- coding: utf-8 -*-
# Copyright (c) 2021, Lin To and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class SalesInvoice(Document):
    def validate(self):
        self.validate_account_types()
        self.validate_item_quantities()

    def before_save(self):
        self.set_item_entry_values()  # Value Per Unit
        self.set_item_entry_cost()
        self.set_invoice_cost()

    def on_submit(self):
        self.remove_items_from_inventory()
        self.add_ledger_entries()

    def validate_account_type(self, account, account_types):
        account_doc = frappe.get_doc("Account", account)
        isnt_valid = account_doc.account_type not in account_types
        if isnt_valid:
            frappe.throw(f"{account} is not from {', '.join(account_types)}")

    def validate_account_types(self):
        self.validate_account_type(self.stock_account, ["Stock"])
        self.validate_account_type(self.receiving_account, ["Income Account"])

    def validate_item_quantities(self):
        for item_entry in self.items:
            try:
                inventory_doc = frappe.get_doc("Inventory", item_entry.item)
            except frappe.DoesNotExistError:
                frappe.throw(f"{self.item} not available.")

            if item_entry.quantity <= 0:
                frappe.throw(f"{item_entry.item} quantity should be more than 0.")
            elif item_entry.quantity > inventory_doc.quantity:
                frappe.throw(f"Insufficient quantity.")

    def set_item_entry_values(self):
        for item_entry in self.items:
            if not item_entry.value:
                item_entry.value = frappe.get_doc("Item", item_entry.item).value

    def set_item_entry_cost(self):
        for item_entry in self.items:
            item_entry.cost = item_entry.value * item_entry.quantity

    def set_invoice_cost(self):
        self.cost = sum([item_entry.cost for item_entry in self.items])

    def remove_items_from_inventory(self):
        for item_entry in self.items:
            inventory_doc = frappe.get_doc("Inventory", item_entry.item)
            inventory_doc.quantity = inventory_doc.quantity - item_entry.quantity
            inventory_doc.save(ignore_permissions=True)

    def get_ledger_entry(self, account, against_account, credit, debit):
        return frappe.get_doc(
            doctype="GL Entry",
            posting_date=self.posting_date,
            account=account,
            against_account=against_account,
            credit=credit,
            debit=debit,
            voucher_type="Purchase Invoice",
            company_name=self.company,
            voucher_number=self.name,
        )

    def add_ledger_entries(self):
        # Create Ledger Entries
        credit_entry = self.get_ledger_entry(
            self.stock_account, self.customer, credit=self.cost, debit=0.0
        )
        debit_entry = self.get_ledger_entry(
            self.receiving_account, self.customer, credit=0.0, debit=self.cost
        )

        # Insert Ledger Entries
        credit_entry.insert(ignore_permissions=True)
        debit_entry.insert(ignore_permissions=True)
