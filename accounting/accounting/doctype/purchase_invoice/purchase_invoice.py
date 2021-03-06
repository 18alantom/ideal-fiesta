# -*- coding: utf-8 -*-
# Copyright (c) 2021, Lin To and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe.model.document import Document


class PurchaseInvoice(Document):
    def validate(self):
        self.validate_account_types()
        self.validate_item_quantities()

    def before_save(self):
        self.set_item_entry_values()  # Value Per Unit
        self.set_item_entry_cost()
        self.set_invoice_cost()

    def on_submit(self):
        self.add_items_to_inventory()
        self.add_ledger_entries()

    def on_cancel(self):
        if self.docstatus == 0:
            return
        self.remove_items_from_inventory()
        self.cancel_ledger_entries()

    def validate_account_type(self, account, account_types):
        account_doc = frappe.get_doc("Account", account)
        isnt_valid = account_doc.account_type not in account_types
        if isnt_valid:
            frappe.throw(f"{account} is not from {', '.join(account_types)}")

    def validate_account_types(self):
        self.validate_account_type(self.stock_account, ["Stock"])
        self.validate_account_type(self.funds_account, ["Payable"])

    def validate_item_quantities(self):
        for item_entry in self.items:
            if item_entry.quantity <= 0:
                frappe.throw(f"{item_entry.item} quantity should be more than 0")

    def set_item_entry_values(self):
        for item_entry in self.items:
            if not item_entry.value:
                item_entry.value = frappe.get_doc("Item", item_entry.item).value

    def set_item_entry_cost(self):
        for item_entry in self.items:
            item_entry.cost = item_entry.value * item_entry.quantity

    def set_invoice_cost(self):
        self.cost = sum([item_entry.cost for item_entry in self.items])

    def add_items_to_inventory(self):
        for item_entry in self.items:
            # Update quantity
            if frappe.db.exists("Inventory", item_entry.item):
                # Update quantity
                inventory_doc = frappe.get_doc("Inventory", item_entry.item)
                inventory_doc.quantity = inventory_doc.quantity + item_entry.quantity
                inventory_doc.save(ignore_permissions=True)
            else:
                # Create new entry
                inventory_doc = frappe.new_doc(doctype="Inventory")
                inventory_doc.item = item_entry.item
                inventory_doc.company = self.company
                inventory_doc.quantity = item_entry.quantity
                inventory_doc.insert(ignore_permissions=True)

    def remove_items_from_inventory(self):
        for item_entry in self.items:
            # Update quantity
            if frappe.db.exists("Inventory", item_entry.item):
                # Update quantity
                inventory_doc = frappe.get_doc("Inventory", item_entry.item)
                inventory_doc.quantity = inventory_doc.quantity - item_entry.quantity
                inventory_doc.save(ignore_permissions=True)

    def get_ledger_entry(
        self, account, against_account, credit, debit, is_for_cancel=False
    ):
        return frappe.get_doc(
            doctype="GL Entry",
            posting_date=self.posting_date,
            account=account,
            against_account=against_account,
            credit=credit,
            debit=debit,
            voucher_type=f"{'Cancel' if is_for_cancel else ''}Purchase Invoice",
            company_name=self.company,
            voucher_number=self.name,
        )

    def add_ledger_entries(self):
        # Create Ledger Entries
        credit_entry = self.get_ledger_entry(
            self.funds_account, self.stock_account, credit=self.cost, debit=0.0
        )
        debit_entry = self.get_ledger_entry(
            self.stock_account, self.seller, credit=0.0, debit=self.cost
        )
        self.insert_ledger_entries(credit_entry, debit_entry)

    def cancel_ledger_entries(self):
        credit_entry = self.get_ledger_entry(
            self.funds_account,
            self.stock_account,
            credit=0.0,
            debit=self.cost,
            is_for_cancel=True,
        )
        debit_entry = self.get_ledger_entry(
            self.stock_account,
            self.seller,
            credit=self.cost,
            debit=0.0,
            is_for_cancel=True,
        )
        self.insert_ledger_entries(credit_entry, debit_entry)

    def insert_ledger_entries(self, credit_entry, debit_entry):
        # Insert Ledger Entries
        for gl_entry in [credit_entry, debit_entry]:
            gl_entry.docstatus = 1
            gl_entry.insert(ignore_permissions=True, ignore_if_duplicate=True)
