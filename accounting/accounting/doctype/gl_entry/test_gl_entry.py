# -*- coding: utf-8 -*-
# Copyright (c) 2021, Lin To and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest
from accounting.test_helpers import delete_all_docs, get_doc_names

invoice_doctypes = ["sales_invoice", "purchase_invoice"]
get_account_name = frappe.get_meta_module("Account").get_account_name


class TestGLEntry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc_handlers = [InvoiceDocHandler(doctype) for doctype in invoice_doctypes]
        for doc_handler in cls.doc_handlers:
            doc_handler.create_and_insert_invoice()
            doc_handler.save_and_submit_docs()

    @classmethod
    def tearDownClass(cls):
        for doc_handler in cls.doc_handlers:
            doc_handler.delete_all_docs()

        del cls.doc_handlers
        for name in get_doc_names(module="Accounting"):
            delete_all_docs(name)

    def test_gl_entry_count(self):
        gl_entries = frappe.get_list("GL Entry")
        num_tr = sum(
            [len(doc_handler._test_records) for doc_handler in self.doc_handlers]
        )
        self.assertEqual(num_tr * 2, len(gl_entries), "Incorrect number of GL Entries")

    def test_account_names(self):
        gl_entries = frappe.get_list(
            "GL Entry",
            fields=["account", "against_account"],
        )
        gl_entries = [(gle["account"], gle["against_account"]) for gle in gl_entries]

        records = []

        for doc_handler in self.doc_handlers:
            records.extend(doc_handler._test_records)

        for record in records:
            company = record[0]
            against_account = record[1]
            account_one = get_account_name(record[3], company)
            account_two = get_account_name(record[4], company)

            self.assertIn((account_one, against_account), gl_entries)
            self.assertIn((account_two, against_account), gl_entries)


class InvoiceDocHandler:
    def __init__(self, doctype):
        test_module = frappe.get_module(
            "accounting.accounting." f"doctype.{doctype}." f"test_{doctype}"
        )
        self.doctype = doctype
        self.doc_handler = test_module.DocHandler()
        self._test_records = test_module._test_records

    def create_and_insert_invoice(self):
        create_and_insert = getattr(
            self.doc_handler, f"create_and_insert_{self.doctype}"
        )
        for (
            company,
            customer,
            items,
            account_one,
            account_two,
            posting_date,
        ) in self._test_records:
            create_and_insert(
                company, customer, items, account_one, account_two, posting_date
            )

    def save_and_submit_docs(self):
        self.doc_handler.save_and_submit_docs()

    def delete_all_docs(self, delete_dependency=False):
        self.doc_handler.delete_all_docs(delete_dependency)
