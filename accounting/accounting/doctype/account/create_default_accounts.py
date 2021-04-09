# -*- coding: utf-8 -*-
# Copyright (c) 2021, Lin To and contributors
# For license information, please see license.txt

import frappe

get_account_name = frappe.get_meta_module("Account").get_account_name

PL = "Profit and Loss"
BS = "Balance Sheet"
AF = "Application of Funds (Assets)"
SF = "Source of Funds (Liabilities)"
EQ = "Equity"
IN = "Income"
EX = "Expenses"

default_root_accounts = {
    AF: ("Asset", 0, BS),
    SF: ("Liability", 1, BS),
    EQ: ("Equity", 1, BS),
    IN: ("Income", 1, PL),
    EX: ("Expense", 0, PL),
}

default_non_root_accounts = {
    AF: [
        ("Bank Account", "Bank"),
        ("Cash", "Cash"),
        ("Stock In Hand", "Stock"),
        ("Debtors", "Receivable"),
    ],
    SF: [("Creditors", "Payable")],
    EQ: [("Capital Stock", "Equity")],
    IN: [("Direct Income", "Income Account")],
    EX: [("Direct Expense", "Expense Account")],
}


def create_default_accounts(company_name):
    if not frappe.db.exists("Company", company_name):
        frappe.throw(f"{company_name} doesn't exist.")

    docs_to_insert = []
    for account in default_root_accounts:
        docs_to_insert.append(_create_root_account_doc(account, company_name))
        for doc in _create_node_account_doc(account, company_name):
            docs_to_insert.append(doc)

    _insert_docs(docs_to_insert)


def _create_root_account_doc(account_name, company_name):
    account_type, is_credit, report_type = default_root_accounts[account_name]
    currency = _get_currency(company_name)
    return frappe.get_doc(
        dict(
            doctype="Account",
            account_name=account_name,
            company=company_name,
            currency=currency,
            account_type=account_type,
            is_credit=is_credit,
            is_group=1,
            report_type=report_type,
        )
    )


def _create_node_account_doc(root_account, company_name):
    _, is_credit, report_type = default_root_accounts[root_account]
    accounts = default_non_root_accounts[root_account]
    parent_account = get_account_name(root_account, company_name)
    currency = _get_currency(company_name)
    docs = []
    for account in accounts:
        account_name, account_type = account
        doc = frappe.get_doc(
            dict(
                doctype="Account",
                account_name=account_name,
                company=company_name,
                currency=currency,
                account_type=account_type,
                is_credit=is_credit,
                is_group=0,
                report_type=report_type,
                parent_account=parent_account,
            )
        )
        docs.append(doc)
    return docs


def _get_currency(company_name):
    return frappe.get_value("Company", company_name, "currency")


def _insert_docs(docs):
    for doc in docs:
        doc.insert(
            ignore_permissions=True,
            ignore_links=False,
            ignore_if_duplicate=False,
            ignore_mandatory=True,
        )
    frappe.db.commit()
