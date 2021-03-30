# -*- coding: utf-8 -*-
# Copyright (c) 2021, Lin To and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest
from accounting.test_helpers import get_doc_names, get_autonamed_items
from accounting.test_helpers import delete_all_docs, check_if_doc_exists


get_account_name = frappe.get_meta_module("Account").get_account_name


class TestPurchaseInvoice(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc_handler = DocHandler()
        for (
            company,
            seller,
            items,
            funds_account,
            stock_account,
            posting_date,
        ) in _test_records:
            cls.doc_handler.create_and_insert_purchase_invoice(
                company, seller, items, funds_account, stock_account, posting_date
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

    def create_and_insert_purchase_invoice(
        self, company, seller, items, funds_account, stock_account, posting_date
    ):
        self._handle_purchase_invoice_dependencies(
            company, seller, items, funds_account, stock_account
        )

        purchase_invoice_doc = frappe.get_doc(
            dict(
                doctype="Purchase Invoice",
                company=company,
                seller=seller,
                items=get_autonamed_items(items),
                funds_account=get_account_name(funds_account, company),
                stock_account=get_account_name(stock_account, company),
                posting_date=posting_date,
            )
        )

        purchase_invoice_doc.insert()
        self.main_docs.append(purchase_invoice_doc)

    def save_and_submit_docs(self):
        for purchase_invoice_doc in self.main_docs:
            purchase_invoice_doc.save()
            purchase_invoice_doc.submit()

    def delete_all_docs(self, delete_dependency=False):
        self._delete_main_docs()
        delete_dependency and self._delete_depenency_docs()

    def _delete_depenency_docs(self):
        for dependency_doc in self.dependency_docs[::-1]:
            dependency_doc.delete()

    def _delete_main_docs(self):
        for purchase_invoice_doc in self.main_docs:
            purchase_invoice_doc.cancel()
            purchase_invoice_doc.delete()

    def _handle_purchase_invoice_dependencies(
        self, company, seller, items, funds_account, stock_account
    ):
        self._check_if_exists_and_insert(
            "Company", dict(name=company, company_name=company)
        )

        self._check_if_exists_and_insert(
            "Seller", dict(name=seller, seller_name=seller)
        )

        for item_entry in items:
            item_name = item_entry["item"]
            self._check_if_exists_and_insert(
                "Item", dict(item_name=item_name, item_group="TestGroup")
            )

        self._check_if_exists_and_insert(
            "Account",
            dict(
                name=get_account_name(funds_account, company),
                account_name=funds_account,
                company=company,
                account_type="Bank",
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
        "_Test Seller 1",
        [
            {
                "doctype": "Invoice Item",
                "item": "_Test Item 1",
                "quantity": 100,
                "value": 5000,
            },
            {
                "doctype": "Invoice Item",
                "item": "_Test Item 2",
                "quantity": 0.5,
                "value": 500,
            },
        ],
        "_Test Account_FA",
        "_Test Account_BA",
        "2019-01-02",
    ],
    [
        "_Test Company",
        "_Test Seller 2",
        [
            {
                "doctype": "Invoice Item",
                "item": "_Test Item 3",
                "quantity": 10,
                "value": 2500,
            },
            {
                "doctype": "Invoice Item",
                "item": "_Test Item 4",
                "quantity": 0.25,
                "value": 700,
            },
        ],
        "_Test Account_FA",
        "_Test Account_BA",
        "2019-01-02",
    ],
]
