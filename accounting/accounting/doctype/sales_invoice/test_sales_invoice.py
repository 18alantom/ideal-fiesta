# -*- coding: utf-8 -*-
# Copyright (c) 2021, Lin To and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest
from accounting.test_helpers import get_doc_names, get_autonamed_items
from accounting.test_helpers import delete_all_docs, check_if_doc_exists
from accounting.test_helpers import get_item_autoname


get_account_name = frappe.get_meta_module("Account").get_account_name


class TestSalesInvoice(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc_handler = DocHandler()
        for (
            company,
            customer,
            items,
            receiving_account,
            stock_account,
            posting_date,
        ) in _test_records:
            cls.doc_handler.create_and_insert_sales_invoice(
                company, customer, items, receiving_account, stock_account, posting_date
            )
        cls.doc_handler.save_and_submit_docs()

    @classmethod
    def tearDownClass(cls):
        cls.doc_handler.delete_all_docs()
        del cls.doc_handler
        for name in get_doc_names(module="Accounting"):
            delete_all_docs(name)

    def test_item_costs(self):
        for d, doc in enumerate(self.doc_handler.main_docs):
            with self.subTest(doc_number=d):
                for i, item_entry in enumerate(doc.items):
                    self.sub_test_item_cost(i, item_entry)

    def test_total_cost(self):
        for d, doc in enumerate(self.doc_handler.main_docs):
            self.sub_test_total_cost(d, doc)

    def sub_test_item_cost(self, item_number, item_entry):
        with self.subTest(item_number=item_number, item_name=item_entry.item):
            cost = item_entry.quantity * item_entry.value
            self.assertEqual(
                cost, item_entry.cost, "Incorrect calculation for item cost."
            )

    def sub_test_total_cost(self, doc_number, doc):
        with self.subTest(doc_number=doc_number):
            cost = sum([i.cost for i in doc.items])
            self.assertEqual(cost, doc.cost, "Incorrect calculation for invoice cost")


class DocHandler:
    def __init__(self):
        self.dependency_docs = []
        self.main_docs = []

    def create_and_insert_sales_invoice(
        self, company, customer, items, receiving_account, stock_account, posting_date
    ):
        self._handle_sales_invoice_dependencies(
            company, customer, items, receiving_account, stock_account
        )

        sales_invoice_doc = frappe.get_doc(
            dict(
                doctype="Sales Invoice",
                company=company,
                customer=customer,
                items=get_autonamed_items(items),
                receiving_account=get_account_name(receiving_account, company),
                stock_account=get_account_name(stock_account, company),
                posting_date=posting_date,
            )
        )

        sales_invoice_doc.insert()
        self.main_docs.append(sales_invoice_doc)

    def save_and_submit_docs(self):
        for sales_invoice_doc in self.main_docs:
            sales_invoice_doc.save()
            sales_invoice_doc.submit()

    def delete_all_docs(self, delete_dependency=False):
        self._delete_main_docs()
        delete_dependency and self._delete_depenency_docs()

    def _delete_depenency_docs(self):
        for dependency_doc in self.dependency_docs[::-1]:
            dependency_doc.delete()

    def _delete_main_docs(self):
        for sales_invoice_doc in self.main_docs:
            sales_invoice_doc.cancel()
            sales_invoice_doc.delete()

    def _handle_sales_invoice_dependencies(
        self, company, customer, items, receiving_account, stock_account
    ):
        self._check_if_exists_and_insert(
            "Company", dict(name=company, company_name=company)
        )

        self._check_if_exists_and_insert(
            "Customer", dict(name=customer, customer_id=customer)
        )

        for item_entry in items:
            item_name = item_entry["item"]
            quantity = item_entry["quantity"]
            self._check_if_exists_and_insert(
                "Item", dict(item_name=item_name, item_group="TestGroup")
            )
            self._check_if_exists_and_insert(
                "Inventory",
                dict(
                    item=get_item_autoname(item_entry),
                    quantity=quantity,
                    company=company,
                ),
            )

        self._check_if_exists_and_insert(
            "Account",
            dict(
                name=get_account_name(receiving_account, company),
                account_name=receiving_account,
                company=company,
                account_type="Receivable",
            ),
        )

        self._check_if_exists_and_insert(
            "Account",
            dict(
                name=get_account_name(stock_account, company),
                account_name=stock_account,
                company=company,
                account_type="Stock",
            ),
        )

    def _check_if_exists_and_insert(self, doctype, doc_dict):
        if not check_if_doc_exists(doctype, doc_dict):
            doc_dict.update(dict(doctype=doctype))
            self._create_and_insert_doc(doc_dict)

    def _create_and_insert_doc(self, doc_dict):
        doc = frappe.get_doc(doc_dict)
        doc.insert(
            ignore_permissions=True,
            ignore_links=True,
            ignore_mandatory=True,
        )
        self.dependency_docs.append(doc)


_test_records = [
    [
        "_Test Company",
        "_Test Customer 1",
        [
            {
                "doctype": "Invoice Item",
                "item": "_Test Item 1",
                "quantity": 90,
                "value": 5100,
            },
            {
                "doctype": "Invoice Item",
                "item": "_Test Item 2",
                "quantity": 0.6,
                "value": 540,
            },
        ],
        "_Test Account_RA",
        "_Test Account_SA",
        "2019-01-03",
    ],
    [
        "_Test Company",
        "_Test Customer 2",
        [
            {
                "doctype": "Invoice Item",
                "item": "_Test Item 3",
                "quantity": 8,
                "value": 2510,
            },
            {
                "doctype": "Invoice Item",
                "item": "_Test Item 4",
                "quantity": 0.20,
                "value": 710,
            },
        ],
        "_Test Account_RA",
        "_Test Account_SA",
        "2019-01-03",
    ],
]
