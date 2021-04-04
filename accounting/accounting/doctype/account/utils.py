# -*- coding: utf-8 -*-
# Copyright (c) 2021, Lin To and contributors
# For license information, please see license.txt

import re
import frappe


def get_report(name, filters):
    return frappe.get_module(f"accounting.accounting.report.{name}.{name}").execute(
        filters, filter_by_date=False
    )


@frappe.whitelist()
def get_children(doctype, parent, company, is_root=False):
    accounts = frappe.get_list(
        doctype,
        fields=_get_fields(is_root),
        filters=_get_filters(parent, company, is_root),
    )

    _add_balance(accounts, company)
    return accounts


def _add_balance(accounts, company):
    filters = dict(company=company)
    # This is hack job, Al doesn't approve.
    _, p_l = get_report("p&l", filters)
    _, b_s = get_report("balance_sheet", filters)
    reports = [*b_s, *p_l]
    reports = {k["account"]: k["amount"] for k in reports}
    reports = unformat_reports(reports)

    for account in accounts:
        acc = account["value"].split(" - ")[0]
        if acc in reports:
            account["balance"] = frappe.format(float(reports[acc]), "Currency")
        else:
            account["balance"] = frappe.format(0, "Currency")


def unformat_reports(reports):
    rep = {}
    for acc, amt in reports.items():
        if acc == "":
            continue
        amt = amt.replace(",", "").split(" ")
        amt = amt[0] if len(amt) == 1 else amt[1]

        acc = re.findall("(?:<\w+>)?([^<>]+)(?:</\w+>)?", acc)[0]
        rep[acc] = amt
    return rep


def _get_fields(is_root):
    return [
        "name as value",
        "is_group as expandable",
        "account_type",
        "report_type",
        "currency",
        "is_credit",
    ] + (["parent_account as parent"] if not is_root else [])


def _get_filters(parent, company, is_root):
    filters = []
    filters += [["company", "=", company]]
    filters += [['ifnull(`parent_account`,"")', "=", "" if is_root else parent]]
    return filters
