# Copyright (c) 2013, Lin To and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe import _


def execute(filters=None, filter_by_date=True):
    records = get_sql_records(filters, filter_by_date)
    if len(records) == 0:
        frappe.throw(_("No values available for set filters"))
    statement = get_statement(records)
    columns, data = get_columns_data(statement)
    return columns, data


def get_columns_data(statement):
    columns = ["Account:Data:200", "Amount:Currency:200"]
    by_type = {}

    for acc in statement:
        acc = statement[acc]
        parent = acc["parent"]
        balance = acc["balance"]
        typ = acc["type"]
        cur = acc["currency"]

        if typ not in by_type:
            by_type[typ] = dict(bal=0, ch=[], par=parent, cur=cur)

        by_type[typ]["bal"] += balance
        by_type[typ]["ch"].append(get_child_row(acc))

    data = []

    for k in ["Income", "Expense"]:
        if k not in by_type:
            continue

        meta = by_type[k]
        par = frappe.bold(meta["par"].split(" - ")[0])
        cur = meta["cur"]
        cb = cur, meta["bal"]
        data.append(get_parent_row(par, *cb))
        for ch in meta["ch"]:
            data.append(ch)

        data.append(get_row(frappe.bold(f"Total {k}"), format_currency(*cb)))
        data.append(get_row("", ""))

    income = 0
    if "Income" in by_type:
        income = by_type["Income"]["bal"]

    expense = 0
    if "Expense" in by_type:
        expense = by_type["Expense"]["bal"]

    diff = income - expense
    diff = format_currency(cur, diff)
    data.append(get_row(frappe.bold("Profit"), diff))
    return columns, data


def get_parent_row(acc, cur, amt):
    bal = format_currency(cur, amt)
    return get_row(acc, bal, 1)


def get_child_row(acc):
    acn = acc["name"]
    cur = acc["currency"]
    amt = acc["balance"]
    bal = format_currency(cur, amt)
    return get_row(acn, bal, 1, 1)


def get_row(acn, bal, is_group=0, indent=0):
    return frappe._dict(
        {"account": acn, "amount": bal, "is_group": is_group, "indent": indent}
    )


def format_currency(cur, amt):
    bal = cur + " "
    bal += frappe.format(amt, "Currency")
    return bal


def get_statement(records):
    statement = {}
    for cr, dr, acc, is_cr, at, an, par, cur in records:
        if acc not in statement:
            statement[acc] = {}
            statement[acc]["balance"] = 0
            statement[acc]["name"] = an
            statement[acc]["currency"] = cur
            statement[acc]["parent"] = par
            statement[acc]["type"] = at.split(" ")[0]
        if is_cr:
            statement[acc]["balance"] += dr
        else:
            statement[acc]["balance"] += cr
    return statement


def get_sql_records(filters, filter_by_date=True):
    query = f"""
    SELECT
        `tabGL Entry`.credit,
        `tabGL Entry`.debit,
        `tabGL Entry`.account,
        `tabAccount`.is_credit,
        `tabAccount`.account_type,
        `tabAccount`.account_name,
        `tabAccount`.parent_account,
        `tabAccount`.currency
    FROM
        `tabGL Entry` JOIN `tabAccount`
        ON `tabGL Entry`.account =`tabAccount`.name
    WHERE
        `tabAccount`.company="{filters['company']}"
        AND
        `tabAccount`.report_type="Profit and Loss"
        AND
        `tabGL Entry`.docstatus=1
    """
    if filter_by_date:
        query += f"""
        AND
        `tabGL Entry`.posting_date BETWEEN
            "{filters['from_date']}"
            AND
            "{filters['to_date']}"
        """
    return frappe.db.sql(query)
